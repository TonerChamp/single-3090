# Profiles

Numbers in this table were measured on the rig in `hardware.md`. A blank speed cell means that profile was not benched. Claimed speeds from other people are in `research/`, and they are labeled as claims.

Driver 595.71.05 for every row dated May 2026. Driver 610.43.02 for the June 19 ik row. The golden 27B MTP row was re-benched on driver 610 at 49.5 / 60.1 TPS (narrative / code) during that comparison. The 48.7 TPS figure is the May 20 measurement on driver 595.

| Profile | Read | Status | Engine | Context | Decode | Use when |
|---|---|---|---|---|---|---|
| `vllm/long-text` | [vllm-long-text.md](vllm-long-text.md) | measured 2026-05-16 | vLLM + Genesis v7.72.2, int4, TQ3 KV | 105K | prefill 1180 at 22K, 300 at 40K | The first config that survived boot. Superseded for daily use |
| `llamacpp/default` | [llamacpp-default.md](llamacpp-default.md) | measured 2026-05-17 | llama.cpp, UD-Q3_K_XL, q4_0 KV | 262K | 37 TPS flat | Long context, vision, cliff-free fallback |
| `vllm/tools-text` | [vllm-tools-text.md](vllm-tools-text.md) | measured 2026-05-17 | vLLM, int4, fp8 KV, MTP n=3 | 75K | 71 narr / 91 code | Tool calls at or under 75K |
| `gemma-4-26b-a4b` | [gemma-26b-a4b.md](gemma-26b-a4b.md) | measured 2026-05-17 | llama.cpp, UD-Q4_K_XL, ngram-mod | 262K | 131 narr / 138 code | Long-context speed |
| `qwen-35b-a3b` | [qwen-35b-a3b.md](qwen-35b-a3b.md) | measured 2026-05-17, June 19 golden | llama.cpp, UD-Q4_K_XL, q4_0 KV, no spec | 262K | 138 / 138 | Fast long-context default |
| `llamacpp-qwen-mtp` | [qwen-27b-mtp.md](qwen-27b-mtp.md) | measured 2026-05-20, June 19 golden | llama.cpp draft-mtp n=2 | 131K | 48.7, then 49.5 / 60.1 on driver 610 | Dense quality under 131K |
| `qwen3.6-27b-ik` | [qwen-27b-ik.md](qwen-27b-ik.md) | measured 2026-06-19 | ik_llama.cpp, IQ4_KS, MTP n=2 | 200K | 61 narr / 76 code | Best dense 27B we ran. Compose file was not saved |

Pick one profile for a session. A swap costs about 10 seconds for a GGUF and about 100–150 seconds cold for vLLM. Per-request routing across profiles is slower than staying put.

Deferred on purpose, never booted here: `vllm/bounded-thinking`, `vllm/long-vision`, `vllm/default`, `vllm/long-text-no-mtp`, `vllm/minimal`, `llamacpp/concurrent`. Reasons are in `research/negative-results.md`.
