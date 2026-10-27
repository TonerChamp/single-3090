# vllm/tools-text

Measured 2026-05-17 on driver 595.71.05. Evidence: measured on this rig.

Same Lorbus int4 weights as long-text. vLLM nightly recorded as `bf610c2f5676` (prefix only). Context 75000, which is the profile default. Leave `MAX_MODEL_LEN` unset. KV `fp8_e5m2`. MTP n=3. GPU util 0.97. Vision off (`--language-model-only`), which returns about 0.86 GiB. Tool parser `qwen3_coder` with auto tool choice and the froggeric chat template. Served name `qwen3.6-27b-autoround`. Compose reference: `compose/upstream/tools-text.yml`. Boot via club-3090 `scripts/switch.sh vllm/tools-text`.

TurboQuant plus MTP plus this hybrid attention stack was already tombstoned upstream on 2026-05-16. fp8 KV is the path that keeps tool calls working. A "swap KV to TQ3 and gain 85/106 TPS" change was tried as research and rejected. See `research/2026-05-17-synthesis.md`.

| Workload | Wall | Decode | Prefill |
|---|---|---|---|
| Narrative 1000 tok, n=5 | 14.0 s | 71.3 TPS (CV 3.1%) | TTFT 109 ms |
| Code 800 tok, n=5 | 8.4 s | 92.7 TPS (CV 2.3%) | TTFT 109 ms |
| 13K + 16 tok | 11.2 s | | 1194 TPS |
| 45K + 30 tok | 41.8 s | | 1077 TPS |
| 58K + 15 tok, fresh | 55.8 s | | 1042 TPS |

MTP acceptance 78–85% on code (per position 0.93 / 0.81 / 0.68) and 54–58% on long-prompt narrative (0.80 / 0.52 / 0.32). Cold boot 152 seconds including image and cudagraph capture. Idle VRAM 21.3 / 24 GiB. 58K prefill 22.7 / 24 GiB. Power 388 W. `max-num-seqs=1`.

Use it for tool-calling work at or under 75K. Past 75K, move to a GGUF profile. There is no vision encoder on this profile.

Footgun: `MAX_MODEL_LEN=105000` left over from long-text exceeds the fp8 budget and OOMs at boot. Comment it, or set 75000, before switching. Restore 105000 before going back to long-text.
