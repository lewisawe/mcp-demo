"""
Backup material for every demo scene, independent of Bedrock quota, model
variance, or venue wifi.

1. `--capture NAME` runs a scene for real (calls Bedrock where the scene
   needs a model) and saves the output to transcripts/NAME.txt. These are
   real runs, not fabricated. Read each one before trusting it.

2. `--play NAME` replays a captured transcript with live-looking pacing so
   you can screen-record it. Record with OBS or your OS recorder, terminal
   maximized, large font. Save the video next to your slides AND on a USB
   stick AND on your phone. A replay of a transcript is a fallback for the
   video, not a substitute for having recorded the video.

Scenes:
    demo1            vulnerable, <IMPORTANT> payload
    demo1-paraphrased  vulnerable, paraphrased payload
    demo2-scope      scoped session
    demo2-approval   human approval, scripted y,n (read file, deny the leak)
    demo2-rugpull    pin and diff (no model call in the blocked half)
    demo2-scan       scanner catches one payload, misses the other

Usage:
    uv run python record_backup.py --capture demo1
    uv run python record_backup.py --play demo1
"""

import argparse
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
TRANSCRIPT_DIR = HERE / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

RUNNERS: dict[str, list[str]] = {
    "demo1": ["run_demo1.py"],
    "demo1-paraphrased": ["run_demo1.py", "--style", "paraphrased"],
    "demo2-scope": ["run_demo2.py", "--scene", "scope"],
    "demo2-approval": ["run_demo2.py", "--scene", "approval", "--answers", "y,n"],
    "demo2-rugpull": ["run_demo2.py", "--scene", "rugpull"],
    "demo2-scan": ["run_demo2.py", "--scene", "scan"],
}

LINE_DELAY = 0.45
PAUSE_MARKERS = (
    "[model->tool]", "[tool->model]", "LEAK LOG", "BLOCKED", "leaked_notes",
    "APPROVAL REQUIRED", "[scan] DROPPED", "[pin]",
)
PAUSE_DELAY = 1.6


def capture(which: str) -> None:
    out_path = TRANSCRIPT_DIR / f"{which}.txt"
    print(f"Running {' '.join(RUNNERS[which])} for a fresh capture (calls Bedrock)...")
    (HERE / "pinned_tools.json").unlink(missing_ok=True)
    result = subprocess.run(
        ["uv", "run", "python", *RUNNERS[which]],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr
    out_path.write_text(output)
    print(f"Captured {len(output.splitlines())} lines to {out_path}")
    print("Read it before trusting it as your backup. Model output varies run to run.")


def play(which: str) -> None:
    path = TRANSCRIPT_DIR / f"{which}.txt"
    if not path.exists():
        print(f"No capture at {path} yet. Run with --capture {which} first.", file=sys.stderr)
        sys.exit(1)
    print("\n" * 2)
    for line in path.read_text().splitlines():
        print(line)
        time.sleep(PAUSE_DELAY if any(m in line for m in PAUSE_MARKERS) else LINE_DELAY)
    print("\n[end of backup playback]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", choices=RUNNERS.keys())
    group.add_argument("--play", choices=RUNNERS.keys())
    args = parser.parse_args()
    capture(args.capture) if args.capture else play(args.play)
