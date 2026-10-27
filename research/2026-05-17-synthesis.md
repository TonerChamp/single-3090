# Research synthesis, 2026-05-17

Evidence label: desk research unless a sentence points at a profile file. The profile files are the measurements. This page is why those measurements were chosen.

Sources we read that day: club-3090, tfriedel/qwen3.6-rtx3090-lab (README, FINDINGS, GEMMA_FINDINGS, TOOL_CALLING_ISSUES), thc1006's spec-decode notes, Hugging Face model cards and discussions, InsiderLLM's Qwen 3.6 guide. SWE-bench figures below are those sources' claims.

## What we kept

**Qwen3.6-27B dense is the quality anchor.** Cited SWE-bench 77.2. Qwen3-Coder-30B-A3B is the May 2025 model, with cited SWE-bench around 50–52 and an Aider polyglot community figure of 60.9. It is a small-VRAM niche, not a replacement for 3.6-27B. The "comparable to Sonnet" line was vendor marketing.

**Qwen3.6-35B-A3B was the new model worth downloading.** Cited single-3090 numbers before we ran it: about 135.7 TPS, UD-Q4_K_XL, 262K, ~20 GB, SWE-bench 73.4. Spec-decode called net-negative on this MoE. We then measured 138/138 TPS and a 200K needle in 106 seconds. That measurement is `profiles/qwen-35b-a3b.md`.

**Gemma 4 26B-A4B on a 3090 is the llama.cpp GGUF plus ngram-mod path**, not vLLM AWQ plus DFlash. DFlash was described as cliffing near 20K on a 3090 and as a 5090-class draft. We measured 131/138 TPS. Sampling that matched the model card was temp 1.0, top-p 0.95, top-k 64. High temperature is the coding setting for this Gemma. Lowering it hurts. Confirmed already present on our compose (test 5B that day).

**Qwen sampling is a client setting on the profiles we ran.** tools-text and llamacpp/default did not pin samplers server-side. Values copied from the Qwen docs at the time: coding with thinking, temp 0.6 / top-p 0.95 / top-k 20 / rep 1.0. General with thinking, temp 1.0 / top-p 0.95 / top-k 20. Non-thinking, temp 0.7 / top-p 0.80 / top-k 20 / rep 1.5.

**froggeric chat template** was the Qwen tool-call fix (native XML `<tool_call><function=name>`). Vendored upstream under the 27B vLLM patches. Test 2 that day passed.

## What we dropped after reading the repo

TurboQuant on tools-text. llama.cpp MTP until PR #22673 landed in the image we pull. Both are in `research/negative-results.md` with the later measurement of MTP.

## Other models that lost the "download next" cut

Devstral Small 2: community SWE-bench near 58, vendor figure 68, dense speed near 33 TPS. GLM-4.7-Flash, Phi-4, Nemotron, and DeepSeek variants were surveyed the same day and did not beat the Qwen pair already on disk for this card. Treat any speed in that survey as someone else's bench.

## Client behavior that changes a local bench

These showed up while mapping coding agents onto one OpenAI-compatible endpoint. They are not rig measurements.

- A server swap of 10–150 seconds is a session choice. Routing a different model per request pays that cost on every turn.
- KV cache reuse dies if the client rewrites the prefix. Stable system prompt, stable tool list order.
- `max_tokens` plus the prompt has to fit under the profile cap. tools-text's useful ceiling is 75000. A client window of 100000 will 400 against it.
- Vision through a long GGUF profile worked on this stack. The tools-text vLLM profile has vision compiled out.
