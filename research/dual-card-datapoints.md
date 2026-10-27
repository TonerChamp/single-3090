# Dual-card numbers we wrote down and did not run

Evidence label: other people's measurements. This rig had one RTX 3090. No NVLink, no second card, no tensor-parallel run.

Kept so a later 48 GB box does not have to rediscover them.

| Source, as of 2026-08-19 | Shape | Decode |
|---|---|---|
| club-3090 `vllm/qwen38-27b-dual-max` | FP8, TP=2 | 67/86 TPS on PCIe, 80/101 on NVLink |
| club-3090 `vllm/qwen38-27b-dual-fast` | W4A8 AutoRound, TP=2 | 72–79 / 105–108. A multi-rail PSU over-current trip was reported on that profile. The note said a single 12 V rail avoided it. That PSU was not this rig's |
| tfriedel TP=2 | W4A16 AWQ | 108–114 / 145–147 |
| SGLang + DSpark | NVLink pair | 124.5 TPS at concurrency 1 |
| club-3090 DFlash2 | 2×3090 | 120/218 |

Ampere tensor-parallel notes attached to those reports: a P2P-patched driver can return wrong data unless `--disable-custom-all-reduce` is set. GDN plus MTP on vLLM wanted `--no-async-scheduling` after long agent runs (Xid 31). PCIe without NVLink, from the May survey of Qwen3.6-27B TP=2, was about a 5% single-stream gain over one card, and up to the high end of a 5–30% band with NVLink and a careful config. NCCL flags those writeups used on PCIe without P2P: `--disable-custom-all-reduce`, `NCCL_P2P_DISABLE=1`, `NCCL_CUMEM_ENABLE=0`.

What 48 GB was expected to unlock, as a list of candidates, not as configs: Qwen3-72B or Qwen3-Coder-32B in fp16, Llama-3.3-70B int4 without offload, GLM-class fp8 around 32B, and the same Qwen or Gemma quants we already run but at higher bits. KV pressure per card drops under TP, which is also the concurrency lever. Two 3090s at the 390 W cap we used are on the order of 700 W sustained. We never measured that.
