---
tags: [mcp, talk, mcp-dev-summit-nairobi, research, claim-audit]
event: MCP Dev Summit Nairobi
date-prepared: 2026-11-10
---

# MCP Security Posture, November 2026: Research and Claim Audit

**Prepared:** November 10, 2026, for the MCP Dev Summit Nairobi talk on tool-description injection.
**Method:** Primary sources were opened and read where possible (spec pages, arXiv abstracts, vendor posts, GitHub issues via API). Search snippets alone are marked as such. Every claim in the talk is graded below.

## Source-quality legend

| Tag | Meaning |
|---|---|
| **P** | Primary: the spec, the paper's own abstract, the vendor's own post, a GitHub record. Read in this session. |
| **V** | Vendor research. Real data, but the vendor sells related products. |
| **PP** | Preprint. Not peer reviewed, or accepted but not yet presented. |
| **AI-CSA** | Cloud Security Alliance Labs notes. Their own banner says "generated with AI assistance, has not undergone official CSA review". Treat as leads, never as authority. |
| **S** | Secondary blog or news. Used only to find primaries. |
| **SNIP** | Seen only as a search snippet. Not read in full. |

---

## 1. Bottom line

1. **The core attack is unchanged and still works.** Hidden instructions in tool metadata reach the model as context. Invariant Labs showed it in April 2025 (P). A November 2026 measurement study found it works against real frameworks with real tool execution (PP).
2. **The protocol still has no mechanism against it.** The 2026-07-28 spec hardened authorization and transport. Its tools page still only says clients must treat tool *annotations* as untrusted. The Security Best Practices page has no section on description injection (P, checked by section list).
3. **The ecosystem is trying to add integrity controls and has not landed one.** The main proposal for digest-pinned tool versions (SEP-1766) was closed on June 24, 2026 (P, GitHub API). A security-annotations proposal (SEP-1075) is closed/dormant (P).
4. **Rug pulls now have data.** A registry census found that 40.6% of multi-version servers silently changed what they advertise between versions (PP).
5. **Defenders have good practice, not a standard.** Pin and diff, scope tools, show arguments, allowlist servers. All client or platform side.

---

## 2. What changed in the spec (read directly)

Source: https://modelcontextprotocol.io/specification/2026-07-28/changelog (P)

Five released versions exist: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25, 2026-07-28 (S for the list, P for the last).

**Security-relevant changes in 2026-07-28:**

| Change | Effect | Addresses description injection? |
|---|---|---|
| Clients must validate `iss` in authorization responses (RFC 9207) | Blocks authorization-server mix-up | No |
| Client credentials bound to the issuing auth server | Stops credential reuse across servers | No |
| Client ID Metadata Documents preferred; Dynamic Client Registration deprecated | Cleaner client identity | No |
| Stateless core, no `initialize`, no session ID | Removes session-hijack surface | No |
| Server-initiated requests replaced by Multi Round-Trip Requests | Server cannot push requests mid-stream | Indirectly (fewer server-to-client channels) |
| Roots, Sampling, Logging deprecated (12-month minimum window) | Sampling was a server-to-LLM channel | Indirectly (my inference, not stated by the spec) |
| `ttlMs` and `cacheScope` required on `tools/list` and other list results | Lists are cacheable | **Raises the question of when a cached description is re-checked.** The spec does not say. |
| Deterministic tool order recommended | Cache and prompt-cache friendly | No |
| `x-mcp-header` mirrors chosen tool parameters into HTTP headers | New server-controlled metadata channel to intermediaries | Not analysed here. Read its constraints before shipping. |

**What the tools page says (P):**
- "Clients MUST consider tool annotations to be untrusted unless they come from trusted servers." Same wording as 2025-06-18.
- "There SHOULD always be a human in the loop with the ability to deny tool invocations."
- Clients SHOULD "show tool inputs to the user before calling the server, to avoid malicious or accidental data exfiltration", validate tool results before passing them to the LLM, and log tool use.
- Servers MUST validate inputs, sanitize outputs, rate limit.

**What it does not say:** nothing requires clients to treat `description` or parameter descriptions as untrusted, to diff them, or to re-approve on change. Several papers and blogs paraphrase the annotation warning as "tool descriptions are untrusted". The current normative text says annotations. If you quote the spec on stage, quote it exactly.

**Security Best Practices page (P, section list):** Confused Deputy, Token Passthrough, SSRF, State Handle Hijacking, Local MCP Server Compromise, OAuth Authorization URL Validation, stdio Transport Security in Proxy Scenarios, Mix-Up Attacks, Localhost Redirect URI Impersonation, CIMD Trust Policies, Scope Minimization. No section on tool poisoning, shadowing, or rug pulls.

**Open proposals (GitHub API, P):**
- SEP-1766 "Digest-Pinned Tool Versioning and Interceptor-Based Validation": **closed 2026-06-24**. Proposed SHA-256 content digests per tool version in `tools/list`.
- SEP-1075 "Security Annotations for MCP Tool Definitions": **closed**, described as dormant over complexity (issue #2745, P).
- IETF individual draft `draft-sharif-mcps-secure-mcp`: proposes tool-definition integrity and signing. The IETF page states it "is not endorsed by the IETF and has no formal standing" (P). Do not present it as a standard.

---

## 3. What attacks are documented (evidence strength)

| Attack | Best evidence | Strength |
|---|---|---|
| **Tool description poisoning** | Invariant Labs, Apr 2025: hidden `<IMPORTANT>` block in an `add` tool leaks `~/.cursor/mcp.json` and SSH keys via a `sidenote` argument (P, V) | Strong demonstration |
| **Shadowing** (a malicious server changes behavior of a trusted server's tool) | Same post: poisoned `add` redirects all `send_email` output to an attacker (P, V) | Strong demonstration |
| **Rug pull** (description changes after approval) | Named in the same post (P, V). Measured drift: 51.1% of multi-version registry servers changed advertised content, 40.6% silently, 4.2% redirected the endpoint host (PP, arXiv 2609.14119) | Drift is measured. "Drift" is not proof of malice. |
| **Measured success rates** | MCPTox (45 servers, 353 tools, 1,348 cases, 20 agents): top model 72.8%, best refusal under 3% (PP, AAAI version). Cross-framework study (12 frameworks, 18 models, 45 scenarios): 22.9% overall (PP, AISec '26) | Strong, but test settings differ |
| **Optimized stealth attacks** | MCP-ITP: up to 84.2% ASR while detection rate dropped to 0.3% (PP) | Shows scanners can be evaded by search |
| **Output/data injection through MCP** (not descriptions) | "Agentjacking" via Sentry events (Tenet; AI-CSA claims 85% success, 2,388 orgs) | Vendor claim. Primary not read. Different class. |
| **Server-side/config command execution** | OX Security (Apr 2026): STDIO config can execute arbitrary commands across SDKs; Anthropic reportedly called it expected behavior (V, The Register S) | Real, disputed as "flaw vs design". Different class. |
| **Hostile server attacks the client** | Pillar Security: MCP Inspector RCE on Windows/WSL during OAuth, GHSA-q978-78c7-phqw, CVE-2026-119025, fixed in Inspector 2.12.0 (P, V) | Confirmed by maintainers |
| **Registry as distribution channel** | MCP registry issue #1563: an entry reported as malware delivery on Aug 9 still listed `active` (P, GitHub record) | One confirmed record. Broader "Shai-Hulud via registry" claims unverified. |

**Important framing for the talk:** description poisoning is one of several ways untrusted MCP servers hurt clients. Say that, so nobody thinks pinning descriptions solves MCP security.

### 3b. OS-level sandboxing of MCP servers (Anthropic sandbox-runtime)

Read in full this session (P):
- https://www.anthropic.com/research/claude-code-sandboxing (Anthropic's announcement blog post)
- https://github.com/anthropics/sandbox-runtime/blob/main/README.md (the tool's own README)
- https://code.claude.com/docs/en/sandbox-environments (Claude Code docs comparing isolation approaches)

**What it is:** `sandbox-runtime` (`srt`), an open-source (beta, research preview) tool from Anthropic that wraps an arbitrary local process, explicitly including local MCP servers, in OS-level filesystem and network restrictions, without requiring a container. Mechanism per platform: `sandbox-exec`/Seatbelt profiles on macOS, `bubblewrap` with network namespace isolation on Linux, a dedicated restricted user account plus a Windows Filtering Platform egress fence on Windows.

**Design posture:** secure-by-default. Write access is denied everywhere unless explicitly allowed (`allowWrite`); network access is denied by default unless explicitly allowed (`allowedDomains`). Read access uses the inverse pattern (allowed everywhere, then explicit deny regions), which the README states directly.

**Usage pattern for MCP specifically** (from the README, reproduced exactly):
```json
// without sandboxing
"filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"] }
// with sandboxing
"filesystem": { "command": "srt", "args": ["npx", "-y", "@modelcontextprotocol/server-filesystem"] }
```
with restrictions declared in a separate `~/.srt-settings.json`.

**Why it does not fix this talk's attack, stated precisely:** Anthropic's own blog post says "sandboxing ensures that even a successful prompt injection is fully isolated, and cannot impact overall user security," in the context of preventing a compromised agent from reaching *unexpected* destinations (e.g. an attacker's exfiltration server that is not the tool's own legitimate endpoint). In this talk's attack, the exfiltration destination *is* the poisoned tool's own server, the one the client is already, legitimately, allowed to talk to. A network allowlist that includes "the server that just sent you this tool definition" does nothing to stop that server receiving data back through a normal, allowed call. The Claude Code docs state this limitation generally: "Isolation also does not change what is sent to the model. Your prompts and the files Claude reads are transmitted to the Anthropic API or your configured provider with or without a sandbox."

**Relationship to the spec's existing guidance:** the spec's "Local MCP Server Compromise" section (already read for this audit, section 2 above) independently SHOULDs "platform-appropriate sandboxing technologies (containers, chroot, application sandboxes, etc.)" for local MCP servers. That section's threat model is explicitly a malicious *startup command* or a malicious server *binary* ("an attacker distributes a malicious payload inside the server itself"), not a legitimate, correctly-running server whose *description text* is the attack vector, which is this talk's subject. Anthropic's tool is a real, shipped answer to the spec's guidance; it is not purpose-built for, and does not claim to solve, description poisoning specifically.

**Status:** explicitly a "beta research preview" per the README. APIs and config formats may change. Covers only local (stdio/subprocess) servers; remote/HTTP MCP servers are outside its scope entirely.

---

## 4. Claim audit

Each claim that appeared in the original submission, the prep notes, my first deck, or the secondary reading.

| # | Claim | Verdict | Evidence and correction |
|---|---|---|---|
| 1 | Invariant Labs disclosed tool poisoning in April 2025 | **Confirmed** | Read the post (P). Updates dated Apr 7 and Apr 11 appear on the page. |
| 2 | "Tool poisoning is the most prevalent client-side MCP vulnerability" (original submission) | **Overstated as a fact** | The phrase comes from the abstract of a STRIDE/DREAD threat-modeling paper (arXiv 2603.22489, PP, snippet read). It is the authors' qualitative ranking, not a measured prevalence. Say "ranked the most prevalent and impactful client-side vulnerability in one threat model". |
| 3 | 22.9% of 9,720 cells vulnerable; 64.9% / 23.0% / 12.1% funnel | **Confirmed** | Abstract read (PP, AISec '26). The funnel percentages are shares of the 2,113 vulnerable cells. |
| 4 | "No framework implements intentional defense" | **Confirmed, with scope** | Abstract: code audit of twelve frameworks. It is the paper's audit, not a universal fact. |
| 5 | Regex scanner rejects 20 of 45 scenarios at 7.2% false positives | **Confirmed** | Abstract (PP). |
| 6 | "All five coordinated disclosures across four vendors were rejected" | **Confirmed from abstract only** | Reported by the authors. Vendors' side not seen. |
| 7 | "84.2% success with auto-approval enabled" (dev.to summary) | **Wrong attribution. Do not use.** | 84.2% is the maximum ASR of an automated *optimization* attack (MCP-ITP) across 12 agents, not an auto-approval statistic. |
| 8 | MCPTox "average 36.5% ASR" | **Not verified** | Appears in an AI-CSA note and a vendor blog. The paper's abstract confirms 72.8% (top model) and <3% best refusal rate, and 1,348 cases (blogs say 1,312). Use the abstract's numbers only. |
| 9 | "More capable models are more susceptible" | **Confirmed for MCPTox, in tension with newer data** | MCPTox abstract says so. The 2026 cross-framework study found model ASR from 0.4% to 49.7%, and one Claude model vulnerable in 8 of 530 cells. Different benchmarks and model eras. Do not state it as a general law. |
| 10 | "Microsoft reports the technique is still observed in 2026" | **Confirmed, but weaker than it sounds** | Microsoft Incident Response, June 30, 2026 (P): pattern "observed in 2026 against a growing range of enterprise agents". The finance-agent walkthrough is an illustrative scenario, and Microsoft says it is "not disclosing details of any specific affected organization". Several articles retell it as a specific incident. It is not documented as one. |
| 11 | "2025-06-18 spec reworked authorization, doesn't stop description poisoning" | **Directionally right, version outdated** | Current spec is 2026-07-28. Same conclusion holds. |
| 12 | "Spec treats tool descriptions as untrusted" (paraphrase in some papers) | **Imprecise** | Normative text covers **annotations**. See section 2. |
| 13 | "No native MCP mechanism to detect or prevent poisoning" (AI-CSA) | **Consistent with the spec** | Verified independently by reading the spec and the closed SEP-1766. |
| 14 | "A signed tool manifests proposal was closed in September 2026" (blog) | **Not confirmed; wrong date and scope** | The relevant SEP-1766 (digest pinning) closed **June 24, 2026**. Signed-manifest research exists as preprints (arXiv 2601.23132) but I found no September SEP closure. |
| 15 | "The scanner everyone recommends dropped hash-based pinning" (blog) | **Not verified** | No primary source found. Do not repeat. |
| 16 | "Anthropic declined to change STDIO behavior" | **Reported by researchers and press** | OX Security says so; The Register notes it depends on "who is telling the story". Anthropic did not respond to The Register. Present as OX's account. |
| 17 | "150M downloads, 200,000 vulnerable instances" | **Vendor estimate** | OX Security numbers (V). Not independently verified. |
| 18 | "99 CVEs published for MCP-related software in 2025" | **Snippet only** | From Microsoft's June 4, 2026 post (SNIP). Read it before using. |
| 19 | Agentjacking: 85% success, 2,388 orgs exposed | **Vendor claim, secondary only** | Tenet Security via AI-CSA and news. Primary not read. |
| 20 | "OWASP ranks prompt injection #1 for LLM apps" | **Not re-verified this session** | An OWASP MCP Top 10 exists (MCP03:2025 Tool Poisoning, P snippet) and is described as a 2025 beta by one source (S). Check the OWASP pages before quoting rankings. |
| 21 | "Layered defense cuts unsafe invocations to 15%, block rate 74%" | **Snippet only, own-testbed** | arXiv 2512.06556 (PP, SNIP). A lead, not a benchmark. |

---

## 5. What is possible now

### Defenders (all client or platform side)

| Control | Status | Notes |
|---|---|---|
| Pin and diff tool definitions | Build it yourself | No protocol support (SEP-1766 closed). Hash name + description + inputSchema at approval. Compare on every `tools/list`, including after cache expiry. |
| Show full arguments before sensitive calls | Spec **SHOULD** | The spec text says to show tool inputs to avoid exfiltration. The Invariant post showed a client hiding the SSH key argument behind a summary. |
| Human in the loop | Spec **SHOULD** | Gate sensitive calls. Blanket approval trains users to click through. |
| Tool scoping, least agency | Practice | Microsoft's guidance: disable "allow all", enable only the tools an agent needs. |
| Server allowlists | Platform feature | Microsoft: tenant-level allowlist of approved publishers (V). |
| Metadata scanners | Available, partial | Regex scanner stopped 20 of 45 scenarios at 7.2% false positives (PP). MCP-ITP shows optimized attacks can slip past detection (PP). Treat as one layer. |
| Sandbox local servers (process-level) | Spec guidance + shipped tool | Spec's Local MCP Server Compromise section SHOULDs this (containers, chroot, app sandboxes), but frames it against malicious startup commands and malicious binaries, not description poisoning. Anthropic's `sandbox-runtime` (open source, beta) does this concretely for any local MCP server: OS-level filesystem and network restriction, secure-by-default. See section 3b below; it does not stop a leak to a destination already on the allowlist. |
| Treat description changes as code changes | Practice | Microsoft: "treat tool descriptions as system prompts" (P, V). |

### Attackers (what a motivated adversary can do today)

- Poison a description, a parameter description, or a schema field.
- Shadow trusted tools from an untrusted server in the same session.
- Change content after approval, bounded only by what the client re-checks.
- Use optimization to evade scanners (MCP-ITP).
- Reach clients through registries and typosquatted or hijacked packages (registry issue #1563; broader supply-chain claims unverified).
- Skip descriptions entirely and inject through tool *outputs* or connected data (agentjacking class).

---

## 6. Recommended changes to the talk

1. **Slide 9 (spec fixed vs not):** replace "Untouched" bullets with exact spec text. Add: "Tools page: annotations must be treated as untrusted. Descriptions: no rule." Add: "Security Best Practices has no section on this."
2. **Slide 10 (related attacks map, done):** the old rug-pull slide became a six-row map (poisoning, shadowing, rug pull, result injection, optimized payloads, other classes). The 40.6% drift figure is row 3. The caching point stays as inference, now only in the notes. Drift is not proof of malice. The 4.2% and "3x higher odds" figures were dropped because their denominators were never confirmed.
3. **Slide 8:** keep the 22.9% funnel. Add one honest line that MCPTox reports far higher rates on older, weaker-aligned models, and that model choice dominates. Do not cite 84.2% as a baseline.
4. **Slide 14:** cite the spec's own SHOULD ("show tool inputs to the user"). It legitimizes the defense.
5. **Add a "what this talk is not" line:** STDIO command execution and OAuth client bugs are separate classes. A listener who knows the OX story will ask.
6. **Remove or soften** the "most prevalent client-side vulnerability" phrase everywhere. Use the attributed version.
7. **Q&A prep:** "Why was digest pinning closed?" I did not read the issue discussion. Read SEP-1766's 15 comments before the talk.
8. **New slide 14 (defense 2b, sandboxing):** covers Anthropic's `sandbox-runtime` as a real, named, shipped implementation of tool-process isolation, with the caveat spoken out loud every time: it does not stop a leak to a destination the client already allowed (the attack in this talk), and it is distinct from the spec's existing sandboxing guidance, which targets malicious binaries, not description poisoning in a legitimate server. See section 3b above for the exact framing.

---

## 7. What I could not verify (open items)

- The SEP-1766 closure reasoning (15 comments unread).
- Tenet's agentjacking primary report and the Sentry response.
- Microsoft's June 4 "99 CVEs" claim in context.
- OWASP Top 10 rankings and the MCP Top 10 status.
- Any comparison of how today's major clients (Claude, Cursor, VS Code, others) display descriptions and arguments. The 2603.22489 paper compares seven clients. Read it before claiming anything about specific products.
- Whether the Anthropic security policy update OX mentions actually changed scope. Read the policy text.
- Primary text of the MCPTox 36.5% average.

## 8. Sources

**Primary**
- MCP spec 2026-07-28 changelog: https://modelcontextprotocol.io/specification/2026-07-28/changelog
- MCP spec tools page: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- MCP spec Security Best Practices: https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices
- SEP-1766: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1766
- SEP-1075: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1075
- Registry issue 1563: https://github.com/modelcontextprotocol/registry/issues/1563
- Invariant Labs disclosure: https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
- Microsoft Incident Response post: https://www.microsoft.com/en-us/security/blog/2026/06/30/securing-ai-agents-ai-tools-move-from-reading-acting/
- Pillar Security (Inspector RCE): https://www.pillar.security/blog/inspecting-the-inspector-rce-in-mcps-official-debugging-tool
- Anthropic, "Beyond permission prompts: making Claude Code more secure and autonomous": https://www.anthropic.com/research/claude-code-sandboxing
- Anthropic, `sandbox-runtime` README: https://github.com/anthropics/sandbox-runtime/blob/main/README.md
- Claude Code docs, "Choose a sandbox environment": https://code.claude.com/docs/en/sandbox-environments

**Preprints**
- Cross-framework measurement: https://arxiv.org/abs/2611.03555
- MCPTox: https://arxiv.org/abs/2508.14925
- MCP-ITP: https://arxiv.org/abs/2601.07395
- Silent drift census: https://arxiv.org/abs/2609.14119
- STRIDE/DREAD threat model: https://arxiv.org/abs/2603.22489
- Layered descriptor defense: https://arxiv.org/abs/2512.06556
- Signed manifests: https://arxiv.org/abs/2601.23132

**Press and vendor**
- The Register on OX Security: https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/
- OWASP MCP03 Tool Poisoning: https://owasp.org/www-project-mcp-top-10/2025/MCP03-2025%E2%80%93Tool-Poisoning
- IETF draft (no formal standing): https://datatracker.ietf.org/doc/html/draft-sharif-mcps-secure-mcp

## See also

- [[talk-plan|talk-plan]] - the run of show these claims feed into
- [[prep/reading-list|reading-list]] - prioritized reading drawn from this audit
- [[prep/preparation-and-qa|preparation-and-qa]] - Q&A built on these claims
- [[prep/slide-deep-dive|slide-deep-dive]] - slide-by-slide use of this evidence
