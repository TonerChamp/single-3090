# llamacpp/default

Measured 2026-05-17 on driver 595.71.05. Evidence: measured on this rig.

Qwen3.6-27B Unsloth `UD-Q3_K_XL` (14 GB) plus `mmproj-F16.gguf` (885 MB). Image `ghcr.io/ggml-org/llama.cpp:server-cuda`. Context 262144. KV q4_0 / q4_0. Flash attention on. Batch `-b 4096 -ub 2048`. One slot. Thinking off by default. Served name `Qwen3.6-27B-UD-Q3_K_XL.gguf`. Compose: `compose/qwen-27b-llamacpp.yml`. `swap/llm-switch.sh llamacpp-qwen` still calls `scripts/switch.sh llamacpp/default` inside the club-3090 checkout, which is this file under that repo's path.

| Workload | Wall | Decode | Prefill |
|---|---|---|---|
| Narrative 1000 tok | 26.9 s | 37.4 TPS | TTFT 200 ms |
| Code 800 tok | 21.7 s | 37.2 TPS | TTFT 196 ms |
| 13K prompt + 16 tok | 11.1 s | | 1236 TPS |
| 100K needle `MAGENTA-OWL-7` | 110.8 s | | recalled |
| 200K needle | 254.9 s | | recalled, prefix cache hit 49K |

Idle and peak VRAM 22.7 / 24 GiB. SM util 97%. Power 383 W. Boot about 10 seconds.

Use it when the session needs more than 131K, when vision is required, or when a vLLM cliff is unacceptable. Leave it when the session is short and tool-heavy (`vllm/tools-text` is more than twice as fast) or when 131K is enough (`qwen-27b-mtp`, and later `qwen-27b-ik`, are faster at higher bits).

The mmproj file has to sit in the parent of `unsloth-q3kxl/`. A Hugging Face download that nests it will fail the preflight until it is moved up. No parallel slots. The card is already full.
