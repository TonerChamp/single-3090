# gemma-4-26b-a4b

Measured 2026-05-17 on driver 595.71.05. Evidence: measured on this rig.

Gemma 4 26B-A4B (4B active). Unsloth UD-Q4_K_XL, 15.9 GB, plus `mmproj-BF16.gguf`, 1.2 GB. Image `ghcr.io/ggml-org/llama.cpp:server-cuda` build `b9102-7d442abf5`. Context 262144. KV fp16, `--kv-unified`, `--parallel 1`, `--ctx-checkpoints 1`. Speculative decoding is `ngram-mod` with no draft model. Flash attention on. `--no-mmproj-offload` keeps the projector on the CPU. Sampling temp 1.0, top-p 0.95, top-k 64. Served name `gemma-4-26b-a4b-gguf`. Compose: `compose/gemma-26b-a4b.yml`. Published on port 8020 so it shares the switcher endpoint. The recipe started from tfriedel's qwen3.6-rtx3090-lab. vLLM AWQ plus DFlash was treated as a 5090-class path and was not run.

| Workload | Wall | Decode | Prefill |
|---|---|---|---|
| Narrative 1000 tok, n=5 | 7.7 s | 131.3 TPS (CV 0.9%) | TTFT 137 ms |
| Code 800 tok, n=5 | 6.0 s | 138.5 TPS (CV 11%) | TTFT 123 ms. Range 130–166 from ngram bursts |
| 17K + 500 tok | 8.5 s | ~120 TPS | 3800 TPS |
| 48K + 15 tok | 14.1 s | | 3406 TPS |
| 69K + 15 tok | 23.5 s | | 2950 TPS |

VRAM 22.8 / 24 GiB at 262K. Boot about 20 seconds. SM util during decode was taken from the upstream findings (~95%), not re-measured here.

`--no-mmap` is required on this build. The UD-Q4_K_XL file has fused expert tensors. With mmap, llama.cpp `b9102` exits with `data is not within the file bounds` even when the SHA256 matches Hugging Face. `--no-mmap` loads it. The older compose this was copied from did not need the flag.

Use it for long-context coding when speed outranks dense quality. `qwen-35b-a3b` later matched the speed with Qwen-lineage quality and became the golden fast profile. Gemma stayed as the fallback. Tool-call extraction is the generic llama.cpp jinja path, not the vLLM `qwen3_coder` parser.
