# single-3090

Measured ways to serve local models on one RTX 3090 with 24 GB. The numbers come from a single rig, specified in [hardware.md](hardware.md). That machine was dismantled on 2026-08-27. This repository is the record, with paths parameterized so another box can boot the same profiles.

The starting point is [club-3090](https://github.com/noonghunna/club-3090) at `da9ef5e` (Apache-2.0). See [ATTRIBUTION.md](ATTRIBUTION.md). Upstream kept moving, including off single-card llama.cpp as a default. What we kept is the layer they do not ship: a model-name swapper, a 503-while-swapping proxy, the compose files we actually benched, and the results.

Weights are not in this repo. Set `MODEL_DIR` to the directory that holds the subfolders listed in `hardware.md`.

## Start here

| You want | Open |
|---|---|
| Which profile for this session | [profiles/INDEX.md](profiles/INDEX.md) |
| The machine the numbers belong to | [hardware.md](hardware.md) |
| What an automated reader must not invent | [AGENTS.md](AGENTS.md) (same index in [CLAUDE.md](CLAUDE.md)) |
| A config that failed so you can skip it | [research/negative-results.md](research/negative-results.md) |

June 19 golden pair, the last known-good daily setup before ik was added beside it:

- `qwen-35b-a3b` at 262K, about 138 tok/s. `compose/qwen-35b-a3b.yml`
- `qwen3.6-27b-mtp` at 131K, about 49–60 tok/s depending on driver and prompt. `compose/qwen-27b-mtp.yml`

`swap/llama-swap.config.yaml` selects between those two by the OpenAI `model` field. The later ik profile was faster and is documented in `profiles/qwen-27b-ik.md`. Its compose file was not preserved.

vLLM profiles (`long-text`, `tools-text`) boot only inside a club-3090 checkout at `da9ef5e`. The YAML in `compose/upstream/` is the reference copy. Read `compose/upstream/README.md` before launching it.

```bash
export MODEL_DIR=/path/to/weights
export CLUB_3090_ROOT=/path/to/club-3090   # only for tools-text and llamacpp-qwen
./swap/llm-switch.sh list
./swap/llm-switch.sh qwen-35b-a3b
curl -s http://127.0.0.1:8020/v1/models
```

## Custom tools

These are the programs written for this rig. llama-swap, llama.cpp, vLLM, and club-3090's `switch.sh` are upstream. The tools below sit on top of them.

**`swap/llm-switch.sh`** swaps the one resident profile. `status`, `list`, `stop`, or a profile name. It stops only containers whose names look like our LLM stacks, waits until VRAM is under 2 GiB, starts the next compose, and blocks until `http://127.0.0.1:8020/v1/models` answers. For `tools-text` it comments `MAX_MODEL_LEN` in the club-3090 `.env`, because a leftover `105000` from long-text OOMs that profile at boot. While the swap runs it holds `/tmp/llm-switch.lock`.

**`swap/llm-proxy.py`** listens on port 8000 and forwards to the container on port 8020. If the lock file exists, `/healthz` and every `/v1` request return 503, so a client in front can fail over for the 10–150 seconds a swap takes. Request timeout is 30 minutes. Body limit is 512 MB. `swap/llm-proxy.service` is the user unit.

**`swap/llm-switch-api.py`** is a small HTTP API on port 9090 so a client can swap profiles without a shell on the rig. `GET /healthz`, `GET /current`, `POST /switch` with `{"profile":"..."}`. The caller sends `Authorization: Bearer $SWITCH_TOKEN`. The call is a no-op when that profile is already up, and it returns when the model endpoint is ready. `swap/llm-switch-api.service` is the unit. Replace `__REPLACE_ME__` before installing it.

**`swap/llama-swap.config.yaml`** plus **`swap/llama-swap.service`** run [llama-swap](https://github.com/mostlygeek/llama-swap) v216 (`2982dd3`). The binary is installed separately, at `~/bin/llama-swap` on the rig. Port 8030. The JSON `model` name starts the matching compose file, checks `/v1/models`, and unloads after 1800 seconds idle. The shipped config is the June 19 golden pair, including the VRAM wait that was added so the 35B model did not start before the previous process had released the card. The service listens on `0.0.0.0` because other machines on a private network called it. On any other network, bind `127.0.0.1`.

**`probes/probe50k.py`** sends one long prompt (a repeated sentence) to port 8020 and prints wall time, prompt tokens, and prefill tokens per second. The model id is hardcoded to `qwen3.6-35b-a3b-gguf`.

**`probes/needle100k.py`** and **`probes/needle200k.py`** bury the string `MAGENTA-OWL-7` in filler sized for about 100K and 200K tokens, ask the model to repeat the code, and print whether it did, plus wall time and effective prefill rate. Same hardcoded model id.

**`probes/toolprobe.py`** runs 10 prompts against three tools (`read_file`, `write_file`, `run_shell`). A pass is exactly one tool call, the expected name, and arguments that parse as JSON. This is the probe behind the 9/10 and 10/10 lines in the profiles.

`.env.example` is the three-line club-3090 env the vLLM profiles used, with `MODEL_DIR` left for you to set and `MAX_MODEL_LEN` commented so it cannot leak into tools-text.

## How to read a number

A speed in `profiles/` was timed on the hardware page's rig, on the date that file states. A speed in `research/` is someone else's claim unless that page says we ran it. Context limits are hard: tools-text dies past 75K, MTP on the dense 27B dies past 131K, and 262K on the A3B leaves a few hundred megabytes free at a 200K prefill. One model at a time. q4_0 KV is what fit the long GGUF profiles. fp8 KV is what kept vLLM tool calls working. TurboQuant plus MTP on this hybrid model did not.
