# qwen-35b-a3b

Measured 2026-05-17 on driver 595.71.05. Still one of the two June 19 golden models on driver 610.43.02. Evidence: measured on this rig.

Qwen3.6-35B-A3B, about 3B active. Unsloth UD-Q4_K_XL, 22.36 GB, plus `mmproj-BF16.gguf`, 903 MB. Same llama.cpp image family as the Gemma profile. Context 262144. KV q4_0 / q4_0, `--kv-unified`, one slot. Spec-decode off. Flash attention on. `--no-mmproj-offload`. `--no-mmap`. `-fit off`. `--no-warmup`. Sampling is not pinned on the server. Served name `qwen3.6-35b-a3b-gguf`. Compose: `compose/qwen-35b-a3b.yml`.

Spec-decode stayed off because A3B expert saturation made it a loss across the configs surveyed (thc1006, 19 configs, a threshold around 94 tokens). A later MTP trial on this model was +8% at Q4_K_XL / 131K and +7.5% at Q3_K_XL / 262K. Neither was promoted. Those compose files are `compose/qwen-35b-a3b-mtp-q4kxl.yml` and `compose/qwen-35b-a3b-mtp-q3kxl.yml`. An ik_llama A3B quant was also slower than this profile (116/137 vs 138/138) and was left alone.

| Workload | Wall | Decode | Prefill |
|---|---|---|---|
| Narrative 1000 tok, n=3 | 7.24 s | 138.2 TPS (CV 0.4%) | TTFT under 100 ms |
| Code 800 tok, n=3 | 5.80 s | 138.0 TPS (CV 0.2%) | |
| 17K + 3 tok | 4.79 s | | 3554 TPS |
| 68K + 3 tok | 23.0 s | | 2962 TPS |
| 135K needle | 58.5 s | | recalled, ~2309 TPS effective |
| 200K needle | 106.1 s | | recalled, ~1885 TPS effective. 2.4× the dense 27B llama.cpp time |
| Tool probe | | | 9/10. The miss was a syslog read that chose a shell tool |

Idle VRAM 23.4 / 24 GiB. Peak at the 200K prefill 23.84 / 24 GiB, 283 MiB free. q4_0 KV is what made 262K fit. Boot about 15 seconds.

SWE-bench 73.4 in the table above is a published claim for the model, not a bench we ran. The dense 27B claim sitting next to it was 77.2.

Use it as the fast long-context model. Sub-128K is comfortable. At 200K there is no room for a second slot or a bigger batch. For tool calls under 75K, `vllm/tools-text` has the parser and MTP built in. This profile's tool path is llama.cpp jinja.
