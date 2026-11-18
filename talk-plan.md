---
tags: [mcp, talk, mcp-dev-summit-nairobi, talk-plan]
event: MCP Dev Summit Nairobi
date: 2026-11-19
slot: 25 minutes
status: in-prep
---

# Talk Plan: Instruction Injection Through MCP Tool Descriptions

**Event:** MCP Dev Summit Nairobi, November 19-20, 2026
**Slot:** 25 minutes (plan about 22 of talking, 3 for questions)
**Deck:** [[slides/slides|slides.md]] (Markdown mirror) or `slides/index.html` (open in a browser; `→`/`←` navigate, `N` toggles speaker notes, `F` fullscreen)

## Corrections to the original submission notes

The submission and prep notes cite the 2025-06-18 spec as current. It is not. The current revision is **2026-07-28** (published July 28, 2026). The deck uses it. If anyone at the summit asks "didn't the new spec fix this?", the answer is on slide 9.

## Verified facts (and where each came from)

| Claim on slides | Source | Confidence |
|---|---|---|
| First public tool-poisoning PoC, Invariant Labs, April 2025 | https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks | Read in search results; open the post before the talk |
| 22.9% overall attack success, 9,720 cells, 12 frameworks, 18 models, 45 scenarios | arXiv:2611.03555 abstract (read directly) | High |
| Funnel 64.9% / 23.0% / 12.1% (shares of vulnerable cells) | Same abstract | High |
| Model ASR range 0.4% to 49.7%; no framework has an intentional defense | Same abstract | High |
| Regex scanner rejects 20 of 45 scenarios at 7.2% false positives | Same abstract | High |
| Paper accepted at AISec '26 (with ACM CCS 2026) | Same abstract | High |
| 2026-07-28: `iss` validation (RFC 9207), credentials bound to issuer, Client ID Metadata Docs preferred and DCR deprecated, `ttlMs`/`cacheScope` on list results | https://modelcontextprotocol.io/specification/2026-07-28/changelog (read in full) | High |
| **10/10 leaked, `tagged` payload; 10/10, `paraphrased` payload** (10 runs each, Haiku 4.5 via Bedrock, `simi-ops`, Nov 11 2026; 95% interval 72% to 100%) | `demo/measure.py` output, this session | Verified by me. One model, one payload, small n. Not comparable to the paper's 22.9% |
| Scoped run: no file tool exists, nothing leaks. The model sometimes narrates chasing the instruction, sometimes not | `demo/transcripts/demo2-scope.txt` | Verified; do not promise the narration |
| Approval scene: `read_file` approved, the `get_weather` call carrying the secret denied, leak log empty | `demo/transcripts/demo2-approval.txt` | Verified |
| Rug pull: v1 pinned, v2 blocked with a diff before any model call | `demo/transcripts/demo2-rugpull.txt` | Verified |
| Scanner drops the `<IMPORTANT>` payload, passes the paraphrase, which leaks | `demo/transcripts/demo2-scan.txt` | Verified. First paraphrase draft leaked 0/10, second 10/10: say so |
| Anthropic's `sandbox-runtime` wraps local MCP servers in OS-level filesystem/network sandboxes; secure-by-default (deny unless allowed) | https://github.com/anthropics/sandbox-runtime (read in full), https://www.anthropic.com/research/claude-code-sandboxing (read in full) | High |
| MCP spec's "Local MCP Server Compromise" section SHOULDs sandboxing (containers, chroot, app sandboxes) for local servers | https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices (read in full) | High |

**Caveats to respect on stage:**
- The 12.1% figure is a share of the *vulnerable* cells, not of all attempts. Say "of the cells that were vulnerable".
- The paper is a preprint (v2, Nov 9, 2026). Call it "a measurement study accepted at AISec", not "established fact".
- Slide 10 is now the related-attacks map. The rug-pull row carries the 40.6% drift figure (preprint, abstract only). The `ttlMs` caching point is **your inference** and now lives only in the slide 10 notes. If you cannot defend it in Q&A, drop it.
- Slide 10, row 5: 84.2% is the best case of a search-optimized attack (MCP-ITP, preprint), not a baseline rate. Say "up to".
- Slide 10, row 4: no numbers on purpose. The vendor reports of result injection were not verified against a primary source.
- The "about 3x higher odds of a high-severity finding" and "4.2% moved endpoint" figures were removed from the slides because the claim audit never confirmed their denominators. They may still appear in `prep/` docs and the deep-dive PDF.
- I did not verify the Microsoft and OWASP claims from your original notes. Leave them off unless you check the primary sources.

## Run of show (25 min)

| Time | Slide | Beat |
|---|---|---|
| 0:00 | 1 | Cold open: "I'll make an agent leak a file because of a weather tool." |
| 0:30 | 2 | Who you are, one concrete credential (fill this in) |
| 1:15 | 3 | Core claim: descriptions are context, the model can't tell docs from orders |
| 2:15 | 4 | Flow diagram, trust boundary sits at the model's context |
| 3:00 | 5 | Poisoned tool code (and: this server has no file access) |
| 3:45 | 6 | **Live demo 1** (2:45, hard stop 6:30) |
| 6:30 | 7 | Why the model obeys (1:00); hand-off to slide 10 |
| 7:30 | 8 | The numbers (22.9% and the funnel); your 10/10 is a worst case |
| 8:45 | 9 | What the new spec fixed vs what it did not (1:00) |
| 9:45 | 10 | **Related attacks map**: poisoning, shadowing, rug pull, result injection, optimized payloads, other classes (1:30; 45 s if behind) |
| 11:15 | 11 | Scanning: paper numbers plus the 30 s offline scan beat (1:15) |
| 12:30 | 12 | Defense 1: pin and diff (and its limit) |
| 13:30 | 13 | Defense 2: scope tools |
| 14:15 | 14 | Defense 2b: OS sandbox (one sentence if behind) |
| 15:00 | 15 | Defense 3: approval with arguments shown |
| 16:00 | 16 | **Live demo 2**: scope, approval, rug pull (3:00, hard stop 19:00) |
| 19:00 | 17 | Five-question audit checklist |
| 20:30 | 18 | Close and three asks; done by 22:00 |

Talking ends around 22:00, leaving about 3 minutes for questions. That
3 minutes is also your cushion if a demo overruns. These timings are
estimates, not measured: do a timed run-through and adjust. If you are
behind, cut in this order: slide 10 down to the six row names (45 s),
slide 14 (one sentence), demo 2 scene 3.
Per-slide speaker notes are embedded in the deck (press `N`).

## Demo status (built and verified, see [[demo/README|demo/README]])

Two servers: a trusted file server and an untrusted weather server with no
file access. The description steers the model into using the other
server's tool, which is the realistic shape of the attack. Measured on
Haiku 4.5: 10/10 for the tagged payload and 10/10 for a reworded one that
passes the regex scanner. Demo 2 has three scenes, one defense each (scope,
approval with arguments shown, pin and diff), plus an offline scanner beat
in slide 11. Real captured transcripts of every scene are in
`demo/transcripts/`. **Those are text, not video: the backup video is
still to be recorded.**

Known gaps, all listed in the README: only Haiku 4.5 measured, sandboxing
not demonstrated, and the model says aloud that it is reading the file.

## Rehearsal checklist

- [x] Fill in slide 2, slide 1 and 17 speaker name and handle (Lewis Sawe, @lewisawe, done)
- [ ] Finish slide 2's one-sentence credential line
- [ ] Add your real speaker bio to the Sessionize profile if still the TODO
- [x] Build the demos and measure the hit rate (10/10 tagged, 10/10 paraphrased, see [[demo/README|demo/README]])
- [ ] Re-run `--capture` and re-measure close to the event date
- [ ] Record backup VIDEOS of all six scenes with `record_backup.py --play`; copy to laptop, USB stick and phone
- [ ] Enable newer Bedrock model access on `simi-ops`, re-run `measure.py --model`, and update slides 6 and 8 with the number you will quote
- [ ] Run `aws sso login` (or check credentials) the morning of the talk; have a plan for venue wifi
- [ ] Check the 2609.14119 and 2601.07395 abstracts and SEP-1766 against the primary sources (slides 9, 10)
- [ ] Open the Pillar Security, OX Security and registry issue 1563 links named on slide 10, so you can answer follow-ups on row 6
- [ ] Decide your answer to "does it work on other vendors' models?" (only Haiku 4.5 is measured)
- [ ] Time a full run-through. Target 22 minutes so you have buffer
- [ ] Run it once from cold with wifi off (the deck uses no external assets, so it should work offline)
- [ ] Publish the demo repo and checklist, then put the real link on slide 17
- [ ] Submit slides to the organizers (required before the event)
- [ ] Test on the venue's display ratio and resolution if you can; the deck locks to 16:9
- [ ] Prepare answers for the Q&A below

## Likely questions

- **"Does a stronger model fix this?"** Partly. The paper shows model resistance varies widely (0.4% to 49.7%) and is the main differentiator, but no model is immune and you can't audit that across every user's setup.
- **"Doesn't the new spec handle this?"** It hardened authorization. It does not inspect description content. See slide 9.
- **"Can a registry verify servers?"** Registries help with provenance and identity. They don't make a description safe, and a verified server can still be compromised or change later.
- **"What about sampling, roots, logging?"** Those are deprecated in 2026-07-28. Not part of this attack.
- **"Does it work on GPT / Gemini / open models?"** Not measured. I only ran Haiku 4.5. The paper's 0.4% to 49.7% range says models differ a lot; test yours.
- **"Why does the weather server need another server?"** It doesn't have file access. A local server could read files itself; the attack that matters steers the model into a trusted server's tool.
- **"Isn't pinning just trust-on-first-use?"** Yes, and the slide says so. It catches change, not a payload from release one. It only helps if a human reads the description at approval time.
- **"Is scanning useless?"** No. It's one layer. It caught 20 of 45 scenarios, with a 7.2% false-positive rate.
- **"Is the 12.1% the real-world number?"** No. It's from a controlled test matrix, and it's a share of vulnerable cells.
- **"Doesn't sandboxing the MCP server just fix this?"** No, and this is the one to get right (see slide 14). OS-level sandboxing (e.g. Anthropic's `sandbox-runtime`) restricts what a server process can touch outside what you've explicitly allowed. It does not stop a poisoned description from convincing the model to send data to a destination you already allowed, which is exactly the attack in this talk: the attacker's server is the legitimate endpoint. Anthropic's own docs say isolation doesn't change what's sent to the model. It's a real, complementary defense against a *different* failure mode (an untrusted server reaching somewhere unexpected), not a substitute for pin-and-diff, scoping, or visible approval.
- **"Is that the same thing as the spec's sandboxing guidance?"** Related but not identical. The spec's "Local MCP Server Compromise" section SHOULDs sandboxing against malicious startup commands or a malicious server *binary*. This talk's attack comes from an otherwise-legitimate, correctly-running server whose *description text* is the payload. Say this distinction explicitly if asked; conflating the two overstates what sandboxing buys you here.

- **"Is the demo tool shadowing?"** Cross-server, yes. Invariant's post describes a malicious server steering how the model uses a trusted server's tools, including passing credentials between servers. In demo 1 the weather text drives the trusted `read_file`. Invariant's own example rewrote `send_email` arguments instead. Same family, different payload.
- **"What about injection through tool results or fetched data?"** Same root cause, different door. Pinning and description scanning never see it. Mitigations are the ones from slides 13 and 15: scope tools, show arguments. The spec only says clients SHOULD validate results, with no method. I did not demo it.
- **"Isn't the STDIO command execution issue the same thing?"** No. That is config or startup command execution (OX Security). Whether it is a flaw or by design is disputed. The fix is sandboxing and not running untrusted configs (slide 14), not pinning descriptions.
- **"If optimized attacks beat scanners, why scan at all?"** Scanning is still a cheap layer (20 of 45 scenarios at 7.2% false positives). Use it, and do not treat it as a boundary.

## Abstract vs talk (things to be ready to explain)

- The abstract says a year of updates "added metadata scanning". The spec has no rule on description content (slide 9). If asked: scanning is client-side tooling, not spec.
- The abstract calls tool poisoning "the most prevalent client-side vulnerability". The source was never verified and the talk does not claim it. Do not repeat it.
- The abstract lists "metadata sanitization" as a defense. The talk shows scanning (and its limit) instead. Say sanitization is the same weakness as scanning if asked.
- Scope: descriptions are one channel. Tool results, resources and prompts need their own answers (slide 7).

## Style reminders for anything you write or say

- Say what you mean directly. No sales pitch for any product. The CFP says those get rejected.
- Label the data fake, the server a toy, and the rug-pull argument as your reading.

## See also

- [[submission|submission.md]] - the original accepted CFP submission
- [[research/mcp-security-posture-2026|mcp-security-posture-2026]] - full claim audit behind every number on the slides
- [[prep/reading-list|reading-list]] - what to actually read before the talk
- [[prep/preparation-and-qa|preparation-and-qa]] - prep checklist and Q&A
- [[prep/glossary|glossary]] - terms used throughout
- [[prep/slide-deep-dive|slide-deep-dive]] - slide-by-slide deep explanation
- [[slides/slides|slides.md]] - Markdown mirror of the deck
