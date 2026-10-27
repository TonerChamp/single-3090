# CLAUDE.md

This file and AGENTS.md carry the same index. Read it before recommending a profile, editing a compose file, or quoting a speed.

## How to use the numbers

The only machine these measurements belong to is described in `hardware.md`. It had one RTX 3090. It no longer exists.

A figure in `profiles/` is a measurement from that rig on the date that file names. A figure in `research/` is someone else's claim unless that page says the rig ran it. Quoted SWE-bench scores are published claims, not benches from this rig.

When a flag is absent from the profile file and from the compose file, leave it out. The ik_llama compose was not saved. Do not reconstruct it past the flags in `profiles/qwen-27b-ik.md`.

`compose/upstream/*.yml` mounts patch paths that exist only inside a club-3090 checkout at `da9ef5e`. Do not `docker compose up` those two files from this directory. `compose/upstream/README.md` has the launch path.

One model occupies the GPU. `MAX_MODEL_LEN=105000` is for `vllm/long-text` only. It OOMs `vllm/tools-text`.

## Index

### Root

| File | What it is |
|---|---|
| `README.md` | What the repo is, how to boot the golden pair, and what each custom tool is for |
| `hardware.md` | CPU, RAM, GPU, driver, power cap, kernel, and weight-folder layout of the measurement rig |
| `AGENTS.md` | This index and the rules for quoting the numbers |
| `CLAUDE.md` | The same index, for sessions that load Claude's project file |
| `ATTRIBUTION.md` | club-3090 commit, sibling repos, weight publishers, and which files are theirs |
| `LICENSE` | Apache-2.0 |
| `.env.example` | `MODEL_DIR`, the CUDA allocator line, and `MAX_MODEL_LEN` commented out |

### profiles/

One file per serving shape. `INDEX.md` is the decision table.

| File | What it is |
|---|---|
| `profiles/INDEX.md` | Workload to profile, with context, decode speed, and status |
| `profiles/vllm-long-text.md` | First working vLLM config. int4, TQ3 KV, 105K, and the eight failed boots that led there |
| `profiles/llamacpp-default.md` | Dense 27B GGUF, 262K, 37 tok/s, vision on, cliff-free fallback |
| `profiles/vllm-tools-text.md` | Dense 27B vLLM, fp8 KV, MTP n=3, 75K, the tool-calling profile |
| `profiles/gemma-26b-a4b.md` | Gemma 4 26B-A4B GGUF, ngram-mod, 262K, the speed fallback |
| `profiles/qwen-35b-a3b.md` | 35B-A3B GGUF, 262K, ~138 tok/s, June 19 golden fast model |
| `profiles/qwen-27b-mtp.md` | Dense 27B llama.cpp MTP n=2, 131K, the other golden model |
| `profiles/qwen-27b-ik.md` | ik_llama IQ4_KS MTP, 200K, fastest dense 27B we measured. Compose not in the repo |

### compose/

Standalone compose files. Set `MODEL_DIR`. Host port 8020 unless llama-swap assigns one.

| File | What it is |
|---|---|
| `compose/qwen-35b-a3b.yml` | Golden A3B llama.cpp stack. Spec-decode off. `--no-mmap` |
| `compose/qwen-27b-mtp.yml` | Golden dense MTP stack at 131K, with `--no-mmap` and `-fit off` |
| `compose/qwen-27b-llamacpp.yml` | club-3090 llama.cpp default (262K, no MTP), from the golden snapshot |
| `compose/gemma-26b-a4b.yml` | Gemma GGUF stack we measured, port 8020 |
| `compose/qwen-35b-a3b-mtp-q4kxl.yml` | A3B MTP trial at Q4_K_XL. Measured, not promoted (+8% at 131K) |
| `compose/qwen-35b-a3b-mtp-q3kxl.yml` | A3B MTP trial at Q3_K_XL. Measured, not promoted (+7.5% at 262K) |
| `compose/qwen3-embedding-0.6b.yml` | Embedding server that worked and was removed because it OOMed the chat model |
| `compose/upstream/README.md` | Why the two vLLM files must be launched from a club-3090 checkout |
| `compose/upstream/long-text.yml` | Upstream vLLM long-text compose, the file behind `profiles/vllm-long-text.md` |
| `compose/upstream/tools-text.yml` | Upstream vLLM tools-text compose, the file behind `profiles/vllm-tools-text.md` |

### swap/

| File | What it is |
|---|---|
| `swap/llm-switch.sh` | One-command profile swap. VRAM wait, health wait, `MAX_MODEL_LEN` guard, sentinel lock |
| `swap/llm-proxy.py` | Port 8000 proxy to port 8020. Returns 503 while `/tmp/llm-switch.lock` exists |
| `swap/llm-proxy.service` | systemd user unit for the proxy |
| `swap/llm-switch-api.py` | Bearer-token HTTP API (`/current`, `/switch`) that runs `llm-switch.sh` |
| `swap/llm-switch-api.service` | systemd user unit for that API. Set `SWITCH_TOKEN` before install |
| `swap/llama-swap.config.yaml` | llama-swap config for the June 19 golden pair, addressed by model name |
| `swap/llama-swap.service` | systemd user unit for llama-swap v216. The binary is not in this repo |

### probes/

All four talk to `http://127.0.0.1:8020` and hardcode the model id `qwen3.6-35b-a3b-gguf`. Change that id to match `/v1/models` before using them on another profile.

| File | What it is |
|---|---|
| `probes/probe50k.py` | One long prompt. Prints prefill tokens per second |
| `probes/needle100k.py` | Recall of a planted code at about 100K tokens |
| `probes/needle200k.py` | The same recall check at about 200K tokens |
| `probes/toolprobe.py` | Ten tool-call prompts, scored pass/fail on name and JSON arguments |

### research/

| File | What it is |
|---|---|
| `research/negative-results.md` | Failed boots, rejected flags, and profiles we chose not to run |
| `research/2026-05-17-synthesis.md` | Why the May profiles were the ones worth measuring, with the claims labeled as claims |
| `research/2026-08-19-qwen38.md` | Qwen3.8-27B desk research. The rig was off. Nothing here was run |
| `research/dual-card-datapoints.md` | Dual-3090 speeds copied from other repos. This rig had one card |
