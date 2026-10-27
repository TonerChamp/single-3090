# What failed, and what we refused to promote

Each item names where the evidence came from.

## Measured on this rig

**vLLM long-text at the published 180K.** Eight boot or runtime failures before 105K worked. Allocator `:False` fragments. `:True` plus a long `MAX_MODEL_LEN` fails the KV check because this driver reserves about 2.87 GiB for the activation profile and leaves 2.17 GiB for KV. Detail in `profiles/vllm-long-text.md`.

**`MAX_MODEL_LEN` carried from long-text into tools-text.** 105000 exceeds the fp8 budget and OOMs at boot. The switcher comments the line.

**Two models on the one GPU.** Ollama on port 11434 auto-loaded `qwen2.5-coder:32b` whenever anything hit it. The chat container then returned HTTP 502. `systemctl disable --now` came back after a reboot. `systemctl mask` is what stuck. If Ollama returns to the same card, it has to unload immediately (`keep_alive: 0`) or llama-swap has to own it.

**Qwen3-Embedding-0.6B Q8_0 beside the chat model.** The embedding server worked: 5.3 s cold, 29 ms warm, 1024-dim vectors, 32K context, about 0.7 GB. A3B at 262K needs the card minus about 300 MB. With the embedder resident only 21.7 GB remained and A3B OOMed at load. Compose kept as `compose/qwen3-embedding-0.6b.yml`. Decision: chat model gets the whole GPU. Embeddings go to a CPU process with `CUDA_VISIBLE_DEVICES` empty.

**262K plus MTP on the dense 27B.** Draft context is about 2.5 GB. It OOMs. 131K is the fit. MTP n=3 acceptance was 52% and lost to n=2.

**A3B MTP, measured and not promoted.** Q4_K_XL at 131K was +8%. Q3_K_XL at 262K was +7.5%. The base profile was already around 138 TPS. Compose files kept, not wired into the switcher.

**ik_llama on the A3B.** 116/137 versus the GGUF golden 138/138.

**Gemma mmap on llama.cpp `b9102`.** Fused expert tensors fail mmap with `data is not within the file bounds` on a file whose hash matches upstream. `--no-mmap` loads it.

## Desk research, then checked against the repo, not re-benched into a win

**TurboQuant 3-bit KV on tools-text.** The compose already says fp8 is required for tool calls with MTP. TurboQuant's verify kernel did not handle Qwen3.6 hybrid attention (DeltaNet plus full attention). Upstream had tombstoned the dual TQ3+MTP compose on 2026-05-16. The "85/106 TPS" writeup was a different serving shape.

**llama.cpp MTP before 2026-05-16.** The stock `server-cuda` image did not have `--spec-type draft-mtp`. A host-native bench of about 47–55 TPS was someone else's binary. We waited for the merge, then measured 48.7 TPS. See `profiles/qwen-27b-mtp.md`.

## Looked at, not booted

`vllm/bounded-thinking` (180K TQ3) would hit the same activation reserve as long-text. `vllm/long-vision` at 198K was unused because coding sessions rarely needed vision at that length. `vllm/default` at 48K is covered by tools-text at 75K. `vllm/long-text-no-mtp` at 200K is slower than the GGUF MoE profiles that already fit 262K. `vllm/minimal` at 32K is shorter than tools-text with no other win. `llamacpp/concurrent` (192K pool, 4 slots) did not match a one-session workload, and the card had no free VRAM for it.

**Qwen3.8-27B** was researched on 2026-08-19 while the rig was down, and the rig was dismantled on 2026-08-27 before any of it ran. See `research/2026-08-19-qwen38.md`.
