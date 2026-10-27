# Attribution

This repo records one single-RTX-3090 rig. The recipes started from other people's work.

[noonghunna/club-3090](https://github.com/noonghunna/club-3090) at commit `da9ef5e` (2026-05-16) is the base. Apache-2.0. The vLLM compose files in `compose/upstream/` are from that checkout, including the June 19 golden snapshot of the tree. `compose/qwen-27b-llamacpp.yml` is their llama.cpp default profile from the same snapshot. Their later catalog (registry, `switch.sh --list`, multi-card Qwen3.8 slugs) is not what we ran. By 2026-08-19 our checkout was about 1,200 commits behind, and they had taken single-card llama.cpp Qwen3.6 slugs off the default list. Issue filed with our early numbers: [club-3090#149](https://github.com/noonghunna/club-3090/issues/149).

[tfriedel/qwen3.6-rtx3090-lab](https://github.com/tfriedel/qwen3.6-rtx3090-lab) supplied the Gemma-4-26B-A4B GGUF direction. We remeasured it and added `--no-mmap` for llama.cpp `b9102`. Their other Qwen vLLM variants (20K, 75K, 125K) were not run. The 125K path wanted `patch_tolist_cudagraph.py` on our driver. We used club-3090's tools-text instead.

[thc1006/qwen3.6-speculative-decoding-rtx3090](https://github.com/thc1006/qwen3.6-speculative-decoding-rtx3090) is the source of "spec-decode is net-negative on the A3B." Our own small MTP trial agreed in direction and was not promoted.

[Sandermage/genesis-vllm-patches](https://github.com/Sandermage/genesis-vllm-patches) is the Genesis tree pinned at v7.72.2 (`7b9fd319`) for the May vLLM profiles. Cliff 2b was [their issue 22](https://github.com/Sandermage/genesis-vllm-patches/issues/22).

Weights: [Lorbus int4 AutoRound](https://huggingface.co/Lorbus/Qwen3.6-27B-int4-AutoRound) for vLLM. Unsloth GGUFs for the llama.cpp profiles. ubergarm IQ4_KS for the ik_llama 27B. froggeric's fixed Qwen chat template for the vLLM tool parser.

[llama-swap](https://github.com/mostlygeek/llama-swap) v216 (`2982dd3`) is the model-name router. We wrote the config and the systemd unit. We did not write llama-swap.

llama.cpp images are `ghcr.io/ggml-org/llama.cpp`. The ik image is `ghcr.io/ikawrakow/ik-llama-cpp`. vLLM images are the nightlies named in the profile files.

Qwen3.8 notes in `research/2026-08-19-qwen38.md` cite club-3090 around `e17e0ee`, syv-ai/qwen38-27b-rtx3090, sudoingX/qwen38-mtp, and the other single-3090 repos named there. None of that was run here.
