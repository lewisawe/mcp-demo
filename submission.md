---
tags: [mcp, talk, mcp-dev-summit-nairobi, submission]
event: MCP Dev Summit Nairobi
date: 2026-11-19
status: accepted
---

# MCP Dev Summit Nairobi - CFP Submission

**Event:** MCP Dev Summit Nairobi
**Event dates:** November 19–20, 2026
**CFP closes:** Monday, August 31, 11:59 PM EAT
**Submission platform:** Sessionize

---

## Session Title

Instruction Injection Through MCP Tool Descriptions

---

## Topic

Security, Identity + Trust

## Session Format

Session Presentation (25 minutes in length)

## Audience Level

Intermediate

---

## Description

_(895 characters — under the 1200 character limit)_

MCP servers describe their tools to an agent using names, descriptions, and parameter schemas, and the client feeds that text straight into the LLM's context, where the model treats it as trusted instruction. That single design fact opens an attack native to MCP, often called tool poisoning: a malicious or compromised server hides instructions inside a tool description, and the agent obeys them.

A year of updates hardened MCP's authorization model and added metadata scanning, yet tool poisoning remains the most prevalent client-side vulnerability, because it targets the model's trust in tool metadata, not the transport layer recent spec changes fixed.

We poison a tool so a harmless-looking get_weather call coaxes an agent into leaking a credentials file, then show why the obvious fixes are only partial and what defense-in-depth actually requires. We finish by re-running the attack against a hardened setup.

---

## Benefits to the Ecosystem

Tool poisoning is the most prevalent client-side vulnerability in MCP, yet most builders connecting agents to servers have never examined the tool metadata their client trusts by default. This talk closes that gap. Rather than a theoretical overview, it gives attendees a working mental model of where the trust boundary sits in an MCP deployment and why recent authorization improvements, valuable as they are, do not address this class of attack.

By showing the attack and its defenses concretely, the talk helps server and client authors ship safer software: sanitizing tool metadata, scoping tools to least privilege, and adding human approval for sensitive calls. A more security-literate builder community means fewer exploitable servers in public registries, which directly protects the ecosystem's reputation as MCP moves into enterprise adoption. The goal is practical: send every attendee home able to audit any MCP server before they connect an agent to it.

---

## Key Takeaways

- How MCP tool metadata reaches the LLM, and why that makes descriptions a trust boundary
- What a poisoned tool definition looks like and why the model obeys it
- Why recent auth/spec updates hardened authorization but not this attack class
- Three practical defenses: metadata sanitization, human-in-the-loop for sensitive tools, and tool scoping
- A mental model for auditing any MCP server before connecting an agent to it

---

## Notes to Reviewers (private)

This is a builder's security talk grounded in the MCP authorization and tool-definition model, not a theoretical overview. The demo uses a purpose-built toy MCP server and a local agent runtime; the "attack" only ever touches my own dummy data, so there is nothing to weaponize and no third-party server is targeted. I intend to bring a live demo with a recorded backup. The defenses shown are ones I implement in the demo, not just a slide of best practices. The talk assumes basic familiarity with how agents call tools; it does not require a security background from the audience.

---

## Speaker Bio / Expertise

_(TODO: add 1–2 honest sentences — what you build, relevant background. Reviewers weight this for security talks.)_

---

## Supporting Context (not submitted — for your own prep)

Current as of mid-2026:

- OWASP still ranks prompt injection as the #1 vulnerability class for LLM applications; tool poisoning is a protocol-native form of it.
- A 2026 STRIDE/DREAD threat-modeling paper names tool poisoning the most prevalent and impactful client-side MCP vulnerability.
- Microsoft security (mid-2026) reports the technique — first disclosed by Invariant Labs, April 2025 — still observed in 2026 against enterprise agents.
- The 2025-06-18 spec reworked authorization (servers no longer issue tokens; a separate OAuth 2.1 authorization server handles it) but does not stop a model from obeying poisoned tool text once it is in context. Different layers.

Verify any specific statistic against its primary source before putting it on a slide.

### Demo shape (to build after acceptance)

1. Tiny MCP server with two tools: benign `get_weather` and sensitive `read_file`.
2. An agent connected to it (a local agent runtime is fine here).
3. Poison `get_weather`'s description to smuggle an instruction to call `read_file` and leak the contents.
4. Apply defenses (metadata sanitization, tool scoping, human approval), re-run, show the attack fail.

Non-deterministic model behavior: pin a model + prompt where it reliably bites, and record a backup video.
