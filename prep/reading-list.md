---
tags: [mcp, talk, mcp-dev-summit-nairobi, prep, reading]
event: MCP Dev Summit Nairobi
---

# Reading List: Instruction Injection Through MCP Tool Descriptions

Ordered by priority. "Read" means the full primary source, not a summary.
"Skim" means you need to know what it says but not quote it precisely.
Everything here is also cited in [[research/mcp-security-posture-2026|mcp-security-posture-2026]]
with a confidence grade; this list is the subset worth your actual time
before November 19.

## Must read in full (your claims rest on these)

1. **Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks"**
   https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
   The original disclosure, April 2025. Slide 5's code example is shaped
   after their `add` tool PoC. Read it so you can answer "where did this
   attack come from?" without hedging, and so your toy server's framing
   matches the real one (hidden `<IMPORTANT>` block, `sidenote`-style
   argument smuggling, the "rug pull" and "shadowing" terms you use on
   slides 10 and 13).

2. **MCP spec, 2026-07-28 changelog**
   https://modelcontextprotocol.io/specification/2026-07-28/changelog
   Everything on slide 9 depends on this being accurate. Read the Major
   Changes and Minor Changes sections in full, not just the two lines on
   the slide. If someone in the room has read the spec more closely than
   you, this is where it would show.

3. **MCP spec, tools page (2026-07-28)**
   https://modelcontextprotocol.io/specification/2026-07-28/server/tools
   The exact wording for "annotations" vs "description" (section 2 of
   [[research/mcp-security-posture-2026|the research doc]]). Also the full Security Considerations section at
   the bottom (`Servers MUST`, `Clients SHOULD`), which slide 14's claim
   about showing tool inputs comes from. Read this one closely enough to
   quote it word for word if challenged.

4. **arXiv 2611.03555, "MCP Tool Poisoning in Agentic AI Frameworks"**
   https://arxiv.org/abs/2611.03555
   Slides 8 and 11 are built on this abstract. You have only read the
   abstract so far, not the full paper. Read at least the methodology
   and results sections before the talk, since this is your main
   quantitative source and the one most likely to get a follow-up
   question ("how was the funnel measured?", "what counts as a
   framework?").

## Should read before the talk (likely Q&A, not yet fully checked)

5. **Anthropic, "Beyond permission prompts: making Claude Code more secure and autonomous"**
   https://www.anthropic.com/research/claude-code-sandboxing
   Source for slide 14 (defense 2b). Already read in full for this
   project, but re-read before the talk so you can state the dual
   filesystem+network isolation requirement precisely, and the 84%
   permission-prompt reduction figure, if asked.

6. **Anthropic, `sandbox-runtime` README**
   https://github.com/anthropics/sandbox-runtime/blob/main/README.md
   The exact `.mcp.json` wrapping pattern on slide 14 comes from here.
   Already read in full. Know the per-platform mechanism
   (sandbox-exec/Seatbelt, bubblewrap, Windows restricted account) well
   enough to answer "how does this actually work?" without hedging.

7. **SEP-1766 discussion thread (15 comments, not yet read)**
   https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1766
   [[research/mcp-security-posture-2026|The research doc]] flags this as the single most likely gap: "why was
   digest pinning closed?" is a natural question for this audience (MCP
   maintainers and contributors will be in the room). Read why it was
   closed, not just that it was closed.

8. **arXiv 2603.22489, "MCP Threat Modeling... Tool Poisoning"**
   https://arxiv.org/html/2603.22489
   This is the source of the "most prevalent client-side vulnerability"
   phrase you deliberately softened ([[research/mcp-security-posture-2026|research doc]], claim #2). It also
   compares seven MCP clients on how they handle tool poisoning. If you
   want to say anything concrete about specific clients (Claude Desktop,
   Cursor, VS Code, etc.) rather than staying abstract, this is the only
   source that would let you do it honestly.

9. **arXiv 2609.14119, "Same Name, Different Server" (registry drift census)**
   https://arxiv.org/abs/2609.14119
   Row 3 of slide 10 uses the 40.6% figure, which comes from the abstract only. Read the full
   methodology section (what counts as "changed what they advertise") so
   you can defend the number if someone asks whether it includes trivial
   version bumps.

## Worth skimming (context, not slide-critical)

10. **Microsoft Incident Response, "Securing AI agents... reading to acting"**
    https://www.microsoft.com/en-us/security/blog/2026/06/30/securing-ai-agents-ai-tools-move-from-reading-acting/
    Confirms the attack is observed in 2026, but the finance-agent example
    is illustrative, not a named incident. Know this distinction; don't
    quote the walkthrough as if it happened to a real company.

11. **The Register, "MCP 'design flaw' puts 200k servers at risk"**
    https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/
    Covers the OX Security STDIO-execution story. This is a *different*
    vulnerability class from your talk (command execution via server
    config, not description poisoning). Skim it so you can correctly say
    "that's a different class of bug" if someone brings it up, without
    pretending to be an expert on it.

12. **Pillar Security, "Inspecting the Inspector" (MCP Inspector RCE)**
    https://www.pillar.security/blog/inspecting-the-inspector-rce-in-mcps-official-debugging-tool
    Another different-class vulnerability (OAuth handshake RCE). Skim
    for the same reason as #11: know it exists, know it's not your topic,
    don't get drawn into explaining it in depth.

13. **MCP spec, Security Best Practices page, "Local MCP Server Compromise" section**
    https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices
    Already read in full for slide 14's caveat. Skim it again before the
    talk so you can state the distinction cleanly: this section SHOULDs
    sandboxing against malicious startup commands and malicious server
    binaries, a different threat model than description poisoning in an
    otherwise-legitimate server.

14. **arXiv 2601.07395, MCP-ITP (optimized tool-poisoning attack)**
    https://arxiv.org/abs/2601.07395
    Source for row 5 of slide 10 (up to 84.2% attack success, detection
    0.3%). Preprint. Read the abstract and check that 84.2% is the best
    case across the agents tested, not an average. Also read how "detection"
    was measured before you quote the 0.3%.

15. **MCP registry issue 1563**
    https://github.com/modelcontextprotocol/registry/issues/1563
    Source for the "malicious registry entries" part of row 6 on slide 10.
    One confirmed record. Do not extend it to broader supply-chain claims.

## Do not cite without reading first

These appeared in earlier drafts or secondary sources and were flagged
in [[research/mcp-security-posture-2026|the research doc]] as unverified. If you want to use any of them, read
the primary source first, not the blog that quotes it.

- "84.2% success with auto-approval enabled" - misattributed, do not use
  (see [[research/mcp-security-posture-2026|research doc]] claim #7). The
  84.2% on slide 10 is a different, correct use: the maximum success of
  MCP-ITP's optimized attack. Always say "up to" and never link it to
  auto-approval.
- "MCPTox average 36.5% ASR" - not confirmed in the paper's own abstract.
- "Signed tool manifests proposal closed in September 2026" - wrong date,
  the real closure (SEP-1766) was June 24.
- Agentjacking "85% success, 2,388 orgs" - vendor claim via Cloud
  Security Alliance notes, primary (Tenet Security) not read.
- Any OWASP Top 10 ranking - the MCP Top 10 project exists but its
  current status wasn't re-verified this session.

## Your own evidence (already verified, no further reading needed)

- [[demo/README|demo/README]] and `demo/transcripts/` - your own measured 10/10 hit
  rate on Haiku 4.5 (two payloads), and the captured transcript of every demo scene. This is
  stronger than anything above because you ran it yourself. Know it well
  enough to describe exactly how it was measured (10 runs, same prompt,
  `measure.py`) if asked.

## See also

- [[talk-plan|talk-plan]] - run of show these sources feed into
- [[research/mcp-security-posture-2026|mcp-security-posture-2026]] - the full claim audit this list is drawn from
- [[prep/preparation-and-qa|preparation-and-qa]] - prep checklist and Q&A
- [[prep/glossary|glossary]] - terms used in these sources and the talk
