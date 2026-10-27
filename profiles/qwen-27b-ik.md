# qwen3.6-27b-ik

Measured 2026-06-19 on driver 610.43.02. Evidence: measured on this rig. The compose file was on the rig and was not copied into the notes, so it is not in `compose/`.

ik_llama.cpp, ikawrakow's fork. Weights `ubergarm/Qwen3.6-27B-GGUF` file `Qwen3.6-27B-MTP-IQ4_KS.gguf`, 16.2 GB, imatrix IQK, about 4 bpw. Image pinned by digest `ghcr.io/ikawrakow/ik-llama-cpp@sha256:5f914f1c…` (prefix only in the notes). The compose lived at `models/qwen3.6-27b/ik-llama/compose/single/ubergarm-iq4ks/mtp.yml` inside the club-3090 checkout after a pull of 488 commits past `da9ef5e`.

Flags recorded from that session: context 200K, q4_0 KV, `-khad` / `-vhad` Hadamard, `--spec-type mtp:n_max=2`, `--merge-qkv`, `--reasoning off`.

Head-to-head against golden `qwen3.6-27b-mtp` is in `profiles/qwen-27b-mtp.md`. Short version: +24% narrative, +27% code, about the same VRAM, 200K instead of 131K, and a higher bit width. An upstream 8-pack quality check was a tie (103 vs 102). That 8-pack is their number, not ours.

It was added as a third llama-swap model next to the two golden entries. Cold swap through port 8030 was 15.6 seconds onto ik and 14.0 seconds back, inside the usual 12–17 second band. The golden pair was byte-identical after the add.

An ik quant of the 35B-A3B was slower than the GGUF golden (116/137 vs 138/138) and was not adopted.

To remove it, delete the `qwen3.6-27b-ik` block from the live llama-swap config and restart the user service. The config shipped here is the pre-ik golden pair, so it already matches that rollback.
