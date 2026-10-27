# llamacpp-qwen-mtp

Measured 2026-05-20 on driver 595.71.05. Re-benched 2026-06-19 on driver 610.43.02 as the golden baseline. Evidence: measured on this rig.

Qwen3.6-27B Unsloth MTP GGUF, UD-Q3_K_XL. The earlier Froggeric MTP file was dropped once the Unsloth MTP publish existed. Image `ghcr.io/ggml-org/llama.cpp:server-cuda` after PR #22673 (merged 2026-05-16). Flags `--spec-type draft-mtp --spec-draft-n-max 2`. Context **131072**. Vision on. By June 19 the compose also had `--no-mmap` and `-fit off`. That is the file in `compose/qwen-27b-mtp.yml`.

262K plus MTP did not fit. The draft context wants about 2.5 GB. n=2 beat n=3 (acceptance at n=3 was 52%).

May 20, against `llamacpp/default` at 37.8 TPS:

| | Result |
|---|---|
| Decode | 48.7 TPS (+29%) |
| 100K needle | 74.5 s, down from 102.7 s |
| Tool probe | 10/10 |
| VRAM | 21.8 GB |
| Draft acceptance | about 80% once warm |

June 19, same card, driver 610, server timings, temp 0.6, compared with ik_llama:

| | This profile, 131K | ik IQ4_KS, 200K |
|---|---|---|
| Narrative decode | 49.5 TPS | 61.4 |
| Code decode | 60.1 TPS | 76.1 |
| Prefill 17K | 1137 | 1161 |
| Prefill 68K | 866 | 920 |
| MTP accept, narrative / code | 62% / 87% | 63% / 90% |
| VRAM | about 21 GB | 21.3 GB |

This profile stayed in the golden llama-swap config as `qwen3.6-27b-mtp` and as the fallback after ik was added. Use it for dense-model agent work at or under 131K when the ik weights are not on disk. Past 131K, use `llamacpp/default` or `qwen-35b-a3b`.
