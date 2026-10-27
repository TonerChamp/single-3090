# Upstream vLLM compose files

`long-text.yml` and `tools-text.yml` are the files that were on the measurement rig inside `noonghunna/club-3090` at commit `da9ef5e` (2026-05-16). They mount Genesis patch scripts with paths relative to that repo (`../../patches/...`).

Run them with that checkout:

```bash
cd "$CLUB_3090_ROOT"
bash scripts/switch.sh vllm/long-text
bash scripts/switch.sh vllm/tools-text
```

`swap/llm-switch.sh` does that for the `tools-text` profile, and it comments `MAX_MODEL_LEN` first. A copied `long-text` value of `105000` OOMs `tools-text` at boot.

Launching these two files with `docker compose` from this directory fails the patch mount. Read them here for the flags that produced the numbers in `profiles/`.
