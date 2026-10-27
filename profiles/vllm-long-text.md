# vllm/long-text

Measured 2026-05-16 on driver 595.71.05. Evidence: measured on this rig.

Qwen3.6-27B, Lorbus int4 AutoRound (`mtp.fc` kept in BF16), vLLM nightly `nightly-01d4d1ad375`, Genesis `7b9fd319` (v7.72.2). Served name `qwen3.6-27b-autoround`. Compose reference: `compose/upstream/long-text.yml`. Boot it from a club-3090 checkout at `da9ef5e`, not from this directory.

Working `.env`:

```
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:512
MAX_MODEL_LEN=105000
```

`gpu-memory-utilization` 0.93. Boot 88 seconds, 124 seconds after a cache clear. Idle VRAM about 22.3 / 24 GiB. A 40K prefill reached 23.85 / 24 GiB.

| Prompt | Time | Prefill |
|---|---|---|
| ~20 tokens | under 1 s | |
| 22,022 tokens | 18.6 s | ~1180 TPS |
| 40,016 tokens | 134 s | ~300 TPS |
| 50K and up | not tested | treated as Cliff 2a risk |

Eight earlier combinations failed. The pattern: with `:False` the allocator fragmented and a Marlin GEMM OOM'd a few hundred MiB into the run. With `:True` and 180K the boot KV check failed because the activation profile reserved 2.87 GiB and left 2.17 GiB for KV. TQ3 is about 17.4 KiB per token, so the boot ceiling was about 124K. 105K is what still had runtime headroom. Lowering `MAX_MODEL_LEN` to 130K did not free KV. The reserve was about 1.3 GiB larger than the maintainer's rig.

Cliff 2b (accumulated context around 21–26K) was still open. PN59's streaming GDN check rejects chunked prefill, and this stack sets `--max-num-batched-tokens=4128`. Tracked then at Sandermage/genesis-vllm-patches#22.

Carry `MAX_MODEL_LEN=105000` into `vllm/tools-text` and that profile OOMs at boot. `swap/llm-switch.sh` comments the line before starting tools-text.
