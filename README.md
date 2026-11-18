# Instruction Injection Through MCP Tool Descriptions

Slides, runnable demo and prep notes for a 25-minute talk at MCP Dev Summit Nairobi, November 19, 2026. Speaker: Lewis Sawe ([@lewisawe](https://github.com/lewisawe)).

The talk shows how an untrusted MCP server can steer a model into misusing a different, trusted server's tools, using nothing but its tool description. The demo reproduces the attack, then runs four defenses and states what each one misses.

## Contents

| Path | What it is |
|---|---|
| `demo/` | Two MCP servers, an agent with defenses, a scanner and runners. See [demo/README.md](demo/README.md). |
| `slides/` | The deck. `index.html` opens in a browser (`→`/`←` navigate, `N` speaker notes, `F` fullscreen). `slides.md` is a Markdown mirror, `slides.pptx` is built by `build_pptx.py`. |
| `prep/` | Slide deep dive, glossary, reading list, and Q&A prep. |
| `research/` | MCP security posture notes the demo is modeled on. |
| `talk-plan.md` | Run of show and verified facts with sources. |
| `cfp.txt`, `submission.md` | The call for proposals and the accepted submission. |

## Quick start

Needs [uv](https://docs.astral.sh/uv/) and AWS credentials with Bedrock access to a Claude model. Details and the model override are in [demo/README.md](demo/README.md).

```bash
cd demo
uv sync
uv run python run_demo1.py                  # the attack
uv run python run_demo2.py --scene scan --offline   # scanner verdicts, no model call
```

`demo/transcripts/` holds captured output of every scene, so you can read the results without running anything.

## Everything in the demo is fake

`demo/dummy_credentials` holds invented values (`AKIAFAKE...`), and the "leak" is a line in a local log file. Nothing leaves the machine. Secret scanners may still flag the key pattern.

## Results and limits

On November 11, 2026, with Claude Haiku 4.5 on Bedrock, both a tagged and a paraphrased payload leaked the fake secret in 10 of 10 runs (95% interval 72% to 100%). That is one model, one hand-written payload and a small sample. It is not comparable to the 22.9% overall attack success rate in [arXiv:2611.03555](https://arxiv.org/abs/2611.03555), which covers 18 models and 45 scenarios.

Each defense has a stated limit, listed in [demo/README.md](demo/README.md). Sandboxing is discussed in the talk but not demonstrated.
