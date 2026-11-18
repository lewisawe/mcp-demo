"""Demo 1: ask the vulnerable setup about the weather, watch the leak.

Two servers are connected: a trusted file reader and an untrusted weather
server. The weather server has no file access. Its description talks the
model into using the OTHER server's tool and carrying the result back.

    uv run python run_demo1.py                      # the <IMPORTANT> payload
    uv run python run_demo1.py --style paraphrased  # same ask, no tell-tale phrasing
"""

import argparse
import asyncio

from agent import LEAK_LOG_PATH, leaked_secret, run_vulnerable_agent


async def main(style: str) -> None:
    LEAK_LOG_PATH.write_text("")  # never show a stale log on stage
    print("=" * 70)
    print(f"DEMO 1: vulnerable client, untrusted weather server ({style} payload)")
    print("=" * 70)
    await run_vulnerable_agent("What is the weather in Nairobi?", style=style)

    print("\n" + "-" * 70)
    if leaked_secret():
        print("LEAK LOG (leak_log.jsonl), proof of what reached the weather server:")
        print(LEAK_LOG_PATH.read_text())
    else:
        print("The secret did NOT reach the weather server this run. The model "
              "didn't bite. Retry once, then cut to the recorded video.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=["tagged", "paraphrased"], default="tagged")
    asyncio.run(main(parser.parse_args().style))
