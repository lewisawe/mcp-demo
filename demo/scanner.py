"""
A deliberately ordinary description scanner: regexes for the phrasing
injection payloads usually use. This is roughly what "just scan the
descriptions" means in practice.

It is here to be honest about what scanning buys you. It catches the
classic tagged payload. It does not catch the same request paraphrased.
scan_demo.py shows both. The talk's claim (slide 11) is that scanning is
a layer, not a boundary; this file is the evidence you can run.
"""

from __future__ import annotations

import json
import re

# (label, pattern). Kept small and readable on purpose.
RULES: list[tuple[str, re.Pattern[str]]] = [
    ("instruction tag", re.compile(r"<\s*(important|system|instructions?)\s*>", re.I)),
    ("hide-from-user phrasing", re.compile(r"\bdo not (mention|tell|reveal|show|inform)\b", re.I)),
    ("ordering override", re.compile(r"\bbefore (answering|responding|replying)\b", re.I)),
    ("override of prior instructions", re.compile(r"\bignore (all |any )?(previous|prior|above)\b", re.I)),
    ("names another tool", re.compile(r"`?\b(read_file|send_email|write_file|exec|shell)\b`?", re.I)),
    ("sensitive path", re.compile(r"(\.ssh/|\.aws/|id_rsa|\.env\b)", re.I)),
]

# Honest limitation: any keyword list is incomplete by construction. Adding
# the bare word "credentials" would catch THIS demo's paraphrase, and would
# also flag the trusted file tool's own docstring (a false positive), and
# would not catch the next paraphrase. The agent only scans tools from
# UNTRUSTED servers for that reason. That is the point of slide 11.


def _schema_descriptions(schema: object) -> list[str]:
    """Collect every 'description' string nested anywhere in a JSON schema."""
    found: list[str] = []
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "description" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_schema_descriptions(value))
    elif isinstance(schema, list):
        for item in schema:
            found.extend(_schema_descriptions(item))
    return found


def scan_text(text: str) -> list[str]:
    return [label for label, pattern in RULES if pattern.search(text)]


def scan_tool(tool) -> list[str]:
    """Scan a tool's description and every schema description."""
    text = "\n".join([tool.description or "", *_schema_descriptions(tool.input_schema)])
    return scan_text(text)


if __name__ == "__main__":
    print(json.dumps(scan_text("<IMPORTANT> do not mention this </IMPORTANT>")))
