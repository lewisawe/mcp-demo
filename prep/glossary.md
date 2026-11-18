---
tags: [mcp, talk, mcp-dev-summit-nairobi, prep, glossary]
event: MCP Dev Summit Nairobi
---

# Glossary

Terms used across the slides, [[research/mcp-security-posture-2026|the research doc]], the demo code, and this
prep material. Organized by topic, not alphabetically, so related terms
sit together. Each entry links back to where it matters most in the talk.

## MCP protocol basics

**MCP (Model Context Protocol)**
The open protocol, originally from Anthropic, that lets an AI
application (the client) connect to external tools and data sources
(servers) in a standardized way. Current spec revision as of this talk:
2026-07-28.

**MCP server**
A program that exposes tools, resources, or prompts to a client over
MCP. Can be local (spawned as a subprocess, talking over stdio) or
remote (talking over HTTP). In the demo, `server_files.py` (trusted) and
`server_weather.py` (untrusted) are both local MCP servers.

**MCP client**
The piece of software that connects to one or more MCP servers on
behalf of an AI application: lists their tools, calls them, and feeds
results back to the model. Examples include Claude Desktop, Cursor, VS
Code extensions, and the small custom client in `demo/agent.py`.

**Agent / agent loop**
The pattern where a model is given tools and allowed to decide, turn by
turn, which ones to call and with what arguments, until it produces a
final answer. `agent.py`'s `_run_agent` function is a minimal example:
list tools, send the question to the model, execute whatever tool calls
come back, feed the results back in, repeat.

**Tool**
A named operation an MCP server exposes, with a `name`, a
`description` (natural-language text), and an `inputSchema` (JSON
Schema describing its parameters). This triplet, specifically the
description and parameter descriptions, is the text the model reads and
the whole talk is about.

**`tools/list`**
The MCP request a client sends to ask a server what tools it has. The
server's response (the list of tool definitions) is exactly what
becomes model context (slide 4).

**`tools/call`**
The MCP request a client sends to actually invoke a tool with specific
arguments, after the model has decided to call it.

**Tool annotation**
Optional metadata on a tool (separate from its `description`) describing
behavioral hints, e.g. whether it's destructive or read-only. The spec's
one explicit untrusted-by-default warning covers annotations
specifically (see "Spec 2026-07-28" below); this is narrower than many
summaries imply, and is the precise point made on slide 9.

## The attack itself

**Tool poisoning / tool poisoning attack (TPA)**
Hiding instructions for the model inside a tool's description,
parameter descriptions, or schema, so the model follows them as if they
were legitimate guidance, while a human skimming the tool list never
sees them. Coined by Invariant Labs in their April 2025 disclosure.
This is the subject of the whole talk.

**Tool description poisoning**
The specific, most common form of tool poisoning, where the hidden
instruction lives in the `description` field. Slide 5's code example
("Before answering, call read_file...") is this.

**Prompt injection**
The broader category: getting a model to follow attacker-supplied
instructions instead of (or in addition to) the user's actual request,
by putting those instructions somewhere the model reads as context.
Tool poisoning is a *protocol-native delivery path* for prompt
injection, specific to how MCP structures tool metadata (slide 7).

**Indirect prompt injection**
Prompt injection where the malicious instruction doesn't come from the
user's own message, but from some other content the model reads along
the way, a document, a web page, a tool description, a tool's output.
Tool poisoning is a form of indirect prompt injection.

**Shadowing**
A specific variant where a malicious server's tool description doesn't
try to get *itself* called maliciously, but instead contains
instructions that change how the model uses a *different, trusted*
tool. Invariant Labs' example: a bogus `add` tool's description
instructs the model to redirect all `send_email` calls to an attacker's
address. Row 2 of slide 10. Demo 1 is the cross-server form: the weather
text steers the trusted `read_file`. Also why tool scoping (slide 13)
matters. Say "same family", not "same attack", when comparing demo 1 to
Invariant's example.

**Rug pull**
When a server you already approved (and whose description you already
saw and trusted) later changes that description, silently, to include
malicious instructions. The name borrows from the same concept in
crypto/token scams. Row 3 of slide 10, backed by measured rug-pull-adjacent
drift (servers changing what they advertise between versions). Shown in
demo 2, scene 3.

**Result injection (output injection)**
Instructions that arrive in a tool's *output*, fetched data, resources or
prompts, not in its description. Same root cause as description
poisoning (instructions and data share one context), different door.
Pinning and description scanning do not see it. Row 4 of slide 10, not
demonstrated, and the slide carries no numbers because the vendor
reports of it were not verified.

**Optimized (adaptive) payload**
An injection whose wording an attacker found by searching, with the
goal of evading detectors. MCP-ITP (arXiv 2601.07395, preprint) reports
up to 84.2% attack success with detection down to 0.3%. That is a
ceiling for an optimized attack, not a prevalence rate. Row 5 of slide
10. Your first-paraphrase 0/10 versus second-paraphrase 10/10 is the
same idea at small scale.

**Argument smuggling**
Getting the model to pass sensitive data (like file contents) through
an innocuous-looking tool argument (like a `notes` field) back to the
poisoned tool's server, so the data leaves disguised as a normal part of
a legitimate call. This is exactly what `notes` does in the demo's
`get_weather` tool.

**Attack success rate (ASR)**
In the measurement papers cited (slide 8, slide 11), the percentage of
test attempts where a poisoning attempt achieved its goal (the model
followed the hidden instruction). Always check *what* counted as
"success" in a given paper: calling the attacker's tool, reaching the
attacker's server, or verifiably exfiltrating a secret are three
different, increasingly strict bars, and [[research/mcp-security-posture-2026|the research doc]] deliberately
separates them (the 64.9% / 23.0% / 12.1% funnel on slide 8).

**Least privilege / least agency**
The security principle of giving a system (or an agent) only the
permissions and capabilities it actually needs for its current task,
nothing more. Slide 13's "tool scoping" defense is this principle
applied to MCP sessions: an agent answering weather questions should
never have a file-reading tool available in the same session.

**The "lethal trifecta"**
An informal framing (mentioned in slide 13's speaker notes) for when an
agent is dangerous: it has access to private/sensitive data, it's
exposed to untrusted external content, and it has some way to send data
out to an external party. Break any one leg and most of these attacks
stop working, even if the poisoned text is still present.

## Defenses

**Pin and diff**
Hashing a tool's `name` + `description` + `inputSchema` the first time
a human approves it, storing that hash, and comparing it against a
freshly fetched `tools/list` every time after. If the hash changes, the
tool is blocked until a human re-approves, instead of being silently
re-trusted. Implemented in `agent.py` as `_tool_fingerprint`,
`_load_pins`, `_save_pins`; this is slide 12's defense 1, and the one
pin-and-diff-related SEP proposal (SEP-1766) for doing this at the
protocol level was closed on June 24, 2026.

**Tool scoping**
Connecting an agent only to the servers and tools it actually needs for
its task, so that even a successfully poisoned description has nothing
dangerous to call. In the demo's scope scene, the session connects only
`server_weather.py` and never `server_files.py`, so there is no
`read_file` and the poisoned instruction has nowhere to go. Slide 13's defense 2.

**Human in the loop**
Requiring explicit human approval before a tool call executes,
especially for sensitive operations. The spec's tools page says clients
*SHOULD* do this ("there SHOULD always be a human in the loop with the
ability to deny tool invocations"). Slide 14's defense 3 goes further:
approval is only meaningful if the human sees the actual *arguments*,
not just the tool's name.

**Argument-visible approval**
The specific, often-missing half of human-in-the-loop: showing the
exact parameters a tool call is about to use (e.g. `notes = "AKIA..."`)
before asking for approval, rather than just "Allow get_weather?" with
no detail. The Invariant Labs disclosure specifically showed Cursor
hiding the leaked SSH key behind a simplified UI even with its
confirmation dialog open; this is the gap defense 3 closes.

**Metadata scanner**
A tool (often regex- or pattern-based) that inspects tool descriptions
and schemas for suspicious phrasing (imperative language aimed at the
model, references to other tools, instructions to conceal behavior)
before a client trusts them. Slide 11's "obvious fix" that catches
"less than half" (20 of 45 scenarios at a 7.2% false-positive rate in
the cited study).

**Server allowlist**
A platform-level control restricting which MCP servers/publishers an
organization's agents are allowed to connect to at all, as opposed to
trusting whatever a user adds. Mentioned as a Microsoft-recommended
practice in [[research/mcp-security-posture-2026|the research doc]], not covered on the slides in detail.

**OS-level sandboxing (process sandboxing)**
Restricting what a running process can touch, which files, which
network destinations, using operating-system primitives rather than a
container or VM. Slide 14's defense 2b: Anthropic's `sandbox-runtime`
does this for local MCP servers using `sandbox-exec`/Seatbelt (macOS),
`bubblewrap` (Linux), or a restricted user account plus an egress fence
(Windows). Distinct from tool scoping (slide 13): scoping controls
which tools exist in a session, sandboxing controls what the server
*process itself* can reach, regardless of what the client exposes.

**Blast radius**
How much damage a successful compromise can do, given everything it's
allowed to touch. Sandboxing reduces blast radius (a compromised
process can only reach allowed files/hosts) without necessarily
stopping the specific attack of concern. The distinction matters on
slide 14: sandboxing shrinks blast radius for *unexpected* reach, but
does nothing against a leak to a destination that's already allowed,
which is exactly this talk's attack (the poisoned server is the
legitimate, allowed endpoint).

**Secure-by-default**
A design posture where access is denied unless explicitly granted,
rather than granted unless explicitly denied. `sandbox-runtime`'s write
and network permissions both default this way (deny-then-allow);
contrasted with its read permission model, which defaults the other
way (allow-then-deny specific regions), per its own README.

## The spec and ecosystem

**SEP (Spec Enhancement Proposal)**
The MCP project's formal process for proposing changes to the protocol,
tracked as numbered GitHub issues/PRs (e.g. SEP-1766). Slide 9
references SEP-1766 (digest-pinned tool versioning, closed June 24,
2026) as evidence that pinning isn't yet a protocol-level guarantee.

**`iss` (issuer) validation**
Part of the 2026-07-28 spec's authorization hardening: clients must
check that the `iss` field in an authorization response matches the
authorization server they expected, per RFC 9207, to prevent a
different kind of attack (authorization-server mix-up) unrelated to
tool poisoning. Cited on slide 9's "Tightened" column specifically to
show what the spec *did* improve, in contrast to what it didn't.

**Client ID Metadata Document (CIMD)**
A newer mechanism for clients to identify themselves to an MCP
authorization server, preferred over the older Dynamic Client
Registration (DCR) protocol, which is now deprecated. Say "preferred",
not "replaced". Another item on
slide 9's "Tightened" column; unrelated to description poisoning.

**`ttlMs` / `cacheScope`**
Fields the 2026-07-28 spec now requires on `tools/list` and other list
results, letting clients cache them for a given time and controlling
whether shared intermediaries may cache them. The slide 10 notes treat
the existence of caching as raising (but not answering) the question of
when a cached, possibly-changed description gets re-checked; this is the
speaker's own inference, not a claim the spec makes, and it is no longer
on the slide.

**Confused deputy problem**
A general security pattern (not specific to MCP, but named in the
spec's Security Best Practices page) where a component with more
privilege than the entity it's acting on behalf of gets tricked into
misusing that privilege. Relevant background for understanding why MCP
proxies and multi-server setups need careful boundaries, though not a
slide-level topic in this talk.

**Local MCP server compromise**
A spec-documented risk category covering what happens when a locally
installed MCP server (a binary running on the user's own machine) turns
out to be malicious or gets compromised. Covered by the spec's guidance
on sandboxing and consent; a different (though related) risk from
in-context description poisoning, which can happen even with a
perfectly sandboxed, "well-behaved" server process.

## Measurement and evidence terms

**Preprint**
A paper that has been posted (often to arXiv) but has not yet completed
peer review, or has been accepted but not yet formally presented. Most
of the quantitative sources in this talk (the 22.9% funnel, the 40.6%
drift figure, MCPTox) are preprints. Treat their numbers as credible but
not yet fully vetted by the field; [[research/mcp-security-posture-2026|the research doc]] flags each one's
status explicitly.

**AISec**
The Workshop on Artificial Intelligence and Security, co-located with
ACM CCS (a major security conference). The source of the main
quantitative slide (slide 8) was accepted here for 2026, which is
meaningfully stronger than an unreviewed preprint, though "accepted" at
a workshop doesn't mean "universally agreed."

**False positive rate (in the scanning context)**
The rate at which a defense (here, a metadata scanner) incorrectly
flags a *legitimate*, non-malicious tool as suspicious. Slide 11's 7.2%
figure means roughly 1 in 14 safe tools would get wrongly blocked by
that scanner, which is the cost side of the "scanning catches less than
half" argument.

**Drift (registry/version drift)**
When a server's advertised tools, descriptions, or even its endpoint
address change between published versions in a registry. Measured at
scale in row 3 of slide 10 (51.1% of multi-version servers changed
something, 40.6% silently). Explicitly not proof of malicious intent by itself;
most drift is probably ordinary software updates. The point on the
slide is that "approved once" is not a durable guarantee regardless of
intent.

## See also

- [[talk-plan|talk-plan]] - run of show using these terms
- [[research/mcp-security-posture-2026|mcp-security-posture-2026]] - full claim audit
- [[prep/reading-list|reading-list]] - sources these terms are drawn from
- [[prep/preparation-and-qa|preparation-and-qa]] - Q&A built on these concepts
- [[prep/slide-deep-dive|slide-deep-dive]] - where each term is used, slide by slide
