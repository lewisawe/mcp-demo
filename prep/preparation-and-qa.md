---
tags: [mcp, talk, mcp-dev-summit-nairobi, prep, qa]
event: MCP Dev Summit Nairobi
---

# Preparation and Q&A Guide

For: "Instruction Injection Through MCP Tool Descriptions", MCP Dev
Summit Nairobi, Nov 19-20 2026. Lewis Sawe, @lewisawe.

This is the operational checklist. [[talk-plan|talk-plan]] has the run of show
and timing; [[prep/reading-list|reading-list]] has what to read; this file has what to
*do* and what to be ready to *answer*.

## 1. What to prepare, in order

### A. Content gaps (you, not me, must fill these)

- [ ] **Slide 2's credential line.** One honest sentence: what you build,
      and the specific MCP thing that went wrong or surprised you. This
      is the single most important unscripted moment in the talk. The
      CFP explicitly said reviewers weight this for security talks, and
      a vague version ("I work with AI agents") will read as filler.
- [ ] **Slide 17's repo link.** Decide whether you're publishing the
      `demo/` folder as-is or cleaning it up first. Either is fine, but
      don't put a link on the slide until it resolves.
- [ ] **Sessionize speaker bio**, if still outstanding from the original
      submission draft.

### B. Technical readiness

- [ ] **Enable Bedrock model access for the 5.x Anthropic models** on
      `simi-ops` (Bedrock console, Model access page), swap `MODEL_ID`
      in `demo/agent.py`, and re-run `measure.py --runs 10`. Current
      numbers are on Haiku 4.5; a current-gen number is more defensible
      and, per the research, likely to show an equal or higher hit rate.
- [ ] **Re-run `measure.py` close to the event date**, not just once.
      Model behavior isn't guaranteed stable release to release, and you
      want the number on the slide to be the number you'd get if someone
      asked you to repeat it live.
- [ ] **Record the backup videos** with `demo/record_backup.py --play`,
      following the steps in `demo/README.md`. Do this with your actual
      laptop and actual screen recorder, not assumed to work.
- [ ] **Re-capture the transcripts** (`--capture` for each of demo1, demo1-paraphrased, demo2-scope, demo2-approval, demo2-rugpull, demo2-scan) right
      before recording, so the backup reflects the exact model/prompt
      pairing you'll use live.
- [ ] **Test the deck with wifi off.** `slides/index.html` has no
      external assets by design, so it should work, but confirm before
      you're relying on it in a venue with uncertain connectivity.
- [ ] **Check the venue's display ratio.** The deck locks to 16:9. If
      the projector is 4:3 or an unusual resolution, know that in
      advance rather than discovering it on stage.

### C. Reading

See [[prep/reading-list|reading-list]]. The four "must read in full" items are not
optional; everything else is triage by how much time you have left.

### D. Rehearsal

- [ ] **Full run-through, timed.** Target 22 minutes of talking inside
      a 25-minute slot, leaving about 3 for questions. Slide 10 is the
      new slide: time it on its own. It should take 1:30, or 45 seconds
      in the short version (six row names plus the "pinning covers rows
      1 to 3" line).
- [ ] **Run both live demos at least 3 times each** in the days before,
      not just once. You want to know what a *failed* run looks like
      (what you say, how you recover) as well as a successful one.
- [ ] **Say the Q&A answers below out loud once**, not just read them.
      The ones under "Hard questions" especially; reading them silently
      and being able to say them fluently under light pressure are
      different skills.
- [ ] **Decide your fallback trigger in advance.** Talk plan already
      says "if the model doesn't bite within one retry, cut to video."
      Decide the exact phrase you'll say when you do that, so it doesn't
      sound like an apology. Suggestion: "This one didn't take. Rather
      than debug live, here's a recorded run." Then move straight to the
      video, no lingering.

## 2. Expected audience

This is an MCP-specific summit; the room likely includes MCP
maintainers, SDK contributors, and people who have read the spec more
recently and more closely than most audiences would. Calibrate for that:

- Assume at least one person has opened SEP-1766 before. Don't bluff
  about why it closed; say "I haven't read the full discussion" if true.
- Assume at least one person works on a client (Claude Desktop, Cursor,
  an IDE integration, a custom agent framework) and may know their own
  product's defenses better than the generic ones on your slides. Invite
  that: "if your client already does this, I'd love to hear it after."
- Assume someone will ask about a *different* MCP vulnerability class
  (STDIO RCE, OAuth bugs, registry supply chain) and expect you to treat
  it as in-scope. Your answer is the "what this talk is not" line: this
  talk is about one specific attack class, tool and description
  poisoning, not MCP security broadly.

## 3. Q&A: likely questions, with answers

### Core questions (from [[talk-plan|talk-plan]], restated with more depth)

**"Does a stronger model fix this?"**
Partly, and only probabilistically. The cross-framework study found
model attack success ranging from 0.4% to 49.7%, so model choice is the
single biggest lever on hit rate. But no model in that study was at 0%,
and MCPTox separately found that *more capable* models were sometimes
*more* susceptible, because the attack exploits good instruction
following rather than a knowledge gap. You cannot pick a model and
declare the problem solved, especially since you don't control which
model your users run.

**"Doesn't the new spec handle this?"**
No. The 2026-07-28 spec tightened who is allowed to connect
(authorization, issuer validation, client identity). It says nothing
about what a connected server's tool descriptions are allowed to say.
Slide 9 has the exact split. If pushed further: the tools page's one
relevant warning covers *annotations*, not *descriptions*, which is a
narrower guarantee than many blog posts imply.

**"Can a registry verify servers?"**
Registries help with provenance (who published this, has it been
scanned) but don't make a description's *content* safe, and a verified
server can still change its description after the fact, which is
exactly what the 40.6% drift figure in row 3 of slide 10 is about. Verification
answers "is this who it claims to be," not "will this always say the
same thing."

**"Is scanning useless?"**
No, but it's a layer, not a boundary. The regex scanner in the paper
caught 20 of 45 scenarios at a 7.2% false-positive rate. That's real
value and real cost, not a solved problem. Separately, MCP-ITP showed an
automated attacker can push detection rates down to 0.3% by optimizing
against the scanner, so a static scanner is something an adversary can
train against if the stakes are high enough.

**"Is the 12.1% the real-world number?"**
No, be precise here if asked: it's a share of the cells that were
already vulnerable in a controlled test matrix (12 frameworks x 18
models x 45 scenarios), not a share of all real-world tool calls or all
attempts. It tells you how often a successful poisoning goes all the way
to exfiltration, not how often poisoning happens in the wild.

**"Doesn't sandboxing the MCP server just fix this? Anthropic has a
tool for this now, right?"**
Yes, Anthropic's `sandbox-runtime` (slide 14) is real, open source, and
specifically calls out MCP servers as a use case. It wraps a local
server in OS-level filesystem and network restrictions. But it does not
stop *this* attack: if the attacker's own server is the allowed network
destination (because that's the legitimate endpoint the client is
already connected to), the sandbox lets the data through, it only
blocks reaching *unexpected* places. Anthropic's own docs say isolation
doesn't change what's sent to the model. This is a blast-radius
control, genuinely useful against a different failure mode (an
untrusted server reaching somewhere it shouldn't), not a substitute for
pin-and-diff, scoping, or visible approval.

**"Isn't that the same sandboxing the spec already recommends?"**
Related, not identical, and worth being precise about if pushed. The
spec's "Local MCP Server Compromise" section SHOULDs sandboxing
against malicious *startup commands* and malicious server *binaries*,
someone distributing a payload inside the server itself. This talk's
attack is a legitimate, correctly-running server whose *description
text* is the payload. Anthropic's tool is a real, shipped answer to the
spec's guidance; it wasn't built for, and doesn't claim to solve,
description poisoning specifically.

### Hard questions specific to this audience

**"Why was SEP-1766 (digest pinning) closed? Doesn't that mean the
maintainers rejected this approach?"**
Read the discussion before the talk (see [[prep/reading-list|reading-list]] item #5). If
you haven't by the time you're asked: "I know it closed on June 24, I
haven't read the full discussion yet, and I don't want to guess at
maintainers' reasoning in front of the people who'd know better than
me. I'd genuinely like to hear it from whoever was in that thread."
That is a better answer than fabricating a reason.

**"You're using a toy server with a deliberately obvious hidden
instruction. Real attacks are subtler. Doesn't that overstate the
problem?"**
Fair challenge, and the honest answer is: the toy server is for
*demonstration* clarity, not because subtler attacks don't exist. MCP-ITP
specifically optimizes poisoned descriptions to evade detection while
keeping success high, pushing detection down to 0.3%. If anything, the
obvious version you're demoing is the *easy* case; the measured success
rates in the paper include far subtler attacks than yours and still land
at 22.9% overall.

**"What about output-based injection, not description-based? Agentjacking,
tool-output poisoning, that kind of thing?"**
That's a related but distinct attack class: instead of poisoning the
tool's metadata, you poison the *data* a trusted tool returns (e.g. an
error-tracking event, a search result). The underlying problem, mixing
instructions and data in one context, is the same family, but the fix
is different (you can't pin a dynamic tool *output* the way you pin a
static description). Slide 10, row 4, already names this class and says
pinning never sees it. Say explicitly that the demos cover the metadata
class, not the output class, that the spec only says clients SHOULD
validate results, and that you haven't independently verified the
specific agentjacking claims circulating (85% success, 2,388 orgs),
since the primary research wasn't available to read directly.

**"Is your demo tool shadowing?"**
Cross-server, yes. Invariant's post describes a malicious server steering
how the model uses a trusted server's tools, including passing
credentials between servers. In demo 1 the weather text drives the
trusted `read_file`. Invariant's own example rewrote `send_email`
arguments instead. Same family, different payload. Slide 10, row 2.

**"Isn't the STDIO command execution issue the same thing?"**
No. That is config or startup command execution (OX Security), and
whether it is a flaw or by design is disputed. The fix is sandboxing and
not running untrusted configs (slide 14), not pinning descriptions.
Slide 10, row 6.

**"If optimized attacks beat scanners, why scan at all?"**
Scanning is still a cheap layer: it caught 20 of 45 scenarios at 7.2%
false positives. Use it, and do not treat it as a boundary. The 84.2% on
slide 10 is a ceiling for a search-optimized attack, not a base rate.

**"Does pinning stop all of these?"**
No. It covers rows 1 to 3 of slide 10 (and only change, not day-one
poison). Result injection needs scoping and visible arguments. Row 6 is a
different class with a different fix.

**"Does your pin-and-diff defense handle a server that's malicious from
the very first connection, before any pin exists?"**
No, and say so plainly. Pin-and-diff is a *change-detection* control: it
catches a server that was fine and later turned hostile (rug pull), or
flags any change at all for re-approval. It does nothing against a
server that's poisoned on day one, before you ever pinned it. That's
what defense 2 (tool scoping) and defense 3 (visible, human-approved
arguments) are for. The three defenses are deliberately layered because
no single one covers every case.

**"Your demo runs locally. What changes in a multi-tenant or hosted
client, where the person approving a tool isn't the person using it?"**
Good question, and the honest answer is: this talk's demo doesn't cover
that case, and the dynamics are materially different. In a shared or
enterprise deployment, the person who clicks "approve" on a new MCP
server often isn't the analyst who later asks it a question (see the
Microsoft finance-agent scenario in the research file, claim 10, which is
exactly this setup). Pin-and-diff still works technically, but *who* gets
shown the diff, and whether they understand what they're looking at,
becomes a harder organizational problem than a technical one.

**"Have you reported any of this to the MCP project, or is this purely
observational?"**
Answer honestly based on what you've actually done. If you haven't
filed anything, say so: "No, I haven't opened an issue myself. The
underlying disclosure is Invariant Labs' from April 2025, and the gap I'm
describing, that descriptions still have no integrity mechanism, is
visible from the public spec and the closed SEP, not something I found
independently." Don't imply you discovered something you didn't.

### Questions where the honest answer is "I don't know, and here's why"

- Anything requiring you to compare specific client products' current
  defenses beyond what arXiv 2603.22489 covers (seven clients, and you
  may not have read the full comparison by the time you're asked).
- Anything about the Microsoft "99 CVEs in 2025" figure beyond the bare
  number; you saw it only as a search snippet, not in context.
- Anything asserting a specific OWASP ranking for prompt injection or
  tool poisoning; not re-verified this session.

For all of these, the pattern is the same: name the specific thing you
haven't verified, say you haven't verified it, and don't fill the gap
with a guess delivered as fact. This audience will respect "I don't
know" far more than a confident wrong answer, and the CFP reviewers
already flagged that over-confident, under-specific claims read as
AI-generated or templated.

## 4. Logistics checklist (from [[talk-plan|talk-plan]], consolidated)

- [ ] Slides submitted to organizers (required for accepted speakers)
- [ ] Speaker bio finalized on Sessionize
- [ ] Code of Conduct acknowledged if not already done at submission
- [ ] Backup videos recorded and tested on the laptop you'll actually
      bring
- [ ] Demo repo published (or decided not to, slide 17 updated either
      way)
- [ ] Laptop charger, adapter for the venue's power/display standard
- [ ] Confirm the venue's AV setup can play local video files if the
      backup is needed (not just screen-share a web page)

## See also

- [[talk-plan|talk-plan]] - run of show and timing
- [[prep/reading-list|reading-list]] - what to read
- [[prep/glossary|glossary]] - terms used throughout this guide
- [[research/mcp-security-posture-2026|mcp-security-posture-2026]] - full claim audit behind every Q&A answer
- [[demo/README|demo/README]] - how the verified demo numbers were produced
