# Measurement rig

Every measured number in this repo comes from one machine. The notes called it `mev`. It was taken apart on 2026-08-27. These specs are that box. They are not the specs of the computer that published this repository.

Motherboard model and PSU model were not written down.

| Part | Recorded value |
|---|---|
| OS | Ubuntu 22.04.5 LTS |
| Kernel, with the May 2026 fingerprint | 5.15.0-179-generic |
| Kernel, on the later host inventory | 5.15.0-176-generic |
| CPU | AMD Ryzen 9 3900X, 12 cores / 24 threads |
| RAM | 31 GiB usable, 8 GiB swap |
| GPU | One NVIDIA RTX 3090, 24 GiB |
| Link | PCIe Gen3 x16 |
| Power cap | 390 W. Display disabled |
| Driver, May 16–20 measurements | 595.71.05 |
| Driver, from the 2026-06-19 snapshot through the ik bench | 610.43.02 |
| Disk, at the May fingerprint | 618 GiB free on ext4. Drive model not recorded |
| CUDA, noted with the allocator investigation | 13.2 (driver side) |
| What can be resident | One LLM container. A second model on the same GPU OOMs |

Observed draw while decoding was 383 W on llama.cpp Q3_K_XL and 388 W on vLLM tools-text, above the 350 W board default, under the 390 W cap.

The activation-profile reserve on this driver was about 1.3 GiB larger than the club-3090 maintainer's reference rig. That is why `vllm/long-text` booted at 105K context here and not at the published 180K. See `profiles/vllm-long-text.md`.

Weights lived in subfolders of one models directory. This repo calls that directory `MODEL_DIR`:

| Subfolder | What it held |
|---|---|
| `qwen3.6-27b-autoround-int4/` | Lorbus int4 AutoRound weights for vLLM |
| `qwen3.6-27b-gguf/unsloth-q3kxl/Qwen3.6-27B-UD-Q3_K_XL.gguf` | 14 GB dense GGUF |
| `qwen3.6-27b-gguf/mmproj-F16.gguf` | 885 MB vision projector. The compose expects this next to the subfolder, not inside it |
| `qwen3.6-27b-gguf-mtp/` | MTP GGUF used by `qwen-27b-mtp.yml` |
| `gemma-26b-a4b-gguf/` | Gemma UD-Q4_K_XL plus `mmproj-BF16.gguf` |
| `qwen3.6-35b-a3b-gguf/` | A3B UD-Q4_K_XL plus `mmproj-BF16.gguf` |
| `qwen3-embedding-0.6b-gguf/` | Embedding GGUF. Loaded, then removed from the GPU. See `research/negative-results.md` |

club-3090 on the rig was commit `da9ef5e` (2026-05-16) through the June 19 golden snapshot. By 2026-08-19 that checkout was about 1,200 commits behind upstream. Upstream had retired the single-card llama.cpp Qwen3.6 slugs from its default catalog. The compose files here kept launching.
