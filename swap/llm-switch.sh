#!/usr/bin/env bash
# llm-switch.sh — swap the resident LLM profile on a single 24 GB GPU.
#
# Profiles:
#   tools-text         vLLM tools-text inside a club-3090 checkout (Qwen3.6-27B int4, 75K)
#   llamacpp-qwen      llama.cpp default inside that same checkout (Qwen3.6-27B Q3_K_XL, 262K)
#   llamacpp-qwen-mtp  compose/qwen-27b-mtp.yml (Q3_K_XL + MTP n=2, 131K)
#   gemma              compose/gemma-26b-a4b.yml
#   qwen-35b-a3b       compose/qwen-35b-a3b.yml
#
# Every profile is published at http://localhost:8020/v1.
# Stops LLM containers, waits until VRAM drops under 2 GiB, then starts the next.
# Non-LLM containers are left running.
#
# tools-text and llamacpp-qwen call club-3090's scripts/switch.sh.
# Set CLUB_3090_ROOT to a checkout of noonghunna/club-3090 at da9ef5e.
# The other three profiles use compose files in this repo.
#
# Usage:
#   llm-switch.sh status
#   llm-switch.sh list
#   llm-switch.sh <profile>
#   llm-switch.sh stop

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUB="${CLUB_3090_ROOT:-${HOME}/club-3090}"
MODEL_DIR="${MODEL_DIR:-${HOME}/models}"
GEMMA_COMPOSE="${ROOT}/compose/gemma-26b-a4b.yml"
QWEN35BA3B_COMPOSE="${ROOT}/compose/qwen-35b-a3b.yml"
QWEN27B_MTP_COMPOSE="${ROOT}/compose/qwen-27b-mtp.yml"
ENDPOINT="http://localhost:8020/v1/models"
SENTINEL="/tmp/llm-switch.lock"

# The proxy on :8000 returns 503 while this file exists.
mark_swapping() { touch "${SENTINEL}"; echo "[switch] sentinel ON  (proxy returns 503)"; }
mark_ready()    { rm -f "${SENTINEL}"; echo "[switch] sentinel OFF (proxy forwards again)"; }

llm_containers() {
  docker ps --format "{{.Names}}" | grep -E "^(vllm-qwen36|vllm-gemma|llama-cpp-qwen36|llamacpp-gemma|llamacpp-qwen36)" || true
}

stop_all() {
  mark_swapping
  local names
  names=$(llm_containers)
  if [[ -z "${names}" ]]; then
    echo "[switch] nothing to stop"
    return 0
  fi
  echo "[switch] stopping: ${names}"
  echo "${names}" | xargs -r docker stop
  echo "${names}" | xargs -r docker rm 2>/dev/null || true
  for _ in $(seq 1 15); do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    if [[ "${used}" -lt 2000 ]]; then break; fi
    sleep 1
  done
  echo "[switch] VRAM idle: ${used} MiB used"
}

wait_ready() {
  local timeout_s=${1:-600}
  local elapsed=0
  while (( elapsed < timeout_s )); do
    if curl -sf "${ENDPOINT}" -o /dev/null 2>/dev/null; then
      local model
      model=$(curl -s "${ENDPOINT}" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"data\"][0][\"id\"])" 2>/dev/null || echo "?")
      echo "[switch] ready (${elapsed}s) — model: ${model}"
      mark_ready
      return 0
    fi
    sleep 5
    elapsed=$(( elapsed + 5 ))
    if (( elapsed % 30 == 0 )); then
      echo "[switch]   ${elapsed}s elapsed, still waiting..."
    fi
  done
  echo "[switch] timeout after ${timeout_s}s"
  return 1
}

ensure_env_for_tools_text() {
  # tools-text OOMs at boot if MAX_MODEL_LEN is above 75000. long-text uses 105000.
  if grep -qE "^MAX_MODEL_LEN=" "${CLUB}/.env" 2>/dev/null; then
    echo "[switch] commenting MAX_MODEL_LEN in ${CLUB}/.env (was: $(grep ^MAX_MODEL_LEN "${CLUB}/.env"))"
    sed -i.bak "s/^MAX_MODEL_LEN=/#MAX_MODEL_LEN=/" "${CLUB}/.env"
  fi
}

start_tools_text() {
  ensure_env_for_tools_text
  cd "${CLUB}"
  bash scripts/switch.sh vllm/tools-text
  wait_ready 600
}

start_llamacpp_qwen() {
  cd "${CLUB}"
  bash scripts/switch.sh llamacpp/default
  wait_ready 300
}

start_llamacpp_qwen_mtp() {
  # llama.cpp MTP (PR #22673, merged 2026-05-16). 131K leaves room for the
  # draft context. 262K plus MTP did not fit in 24 GB.
  cd "$(dirname "${QWEN27B_MTP_COMPOSE}")"
  CTX_SIZE=131072 MTP_N_MAX=2 PORT=8020 MODEL_DIR="${MODEL_DIR}" \
    docker compose -f "$(basename "${QWEN27B_MTP_COMPOSE}")" up -d
  wait_ready 300
}

start_gemma() {
  cd "$(dirname "${GEMMA_COMPOSE}")"
  MODEL_DIR="${MODEL_DIR}" docker compose -f "$(basename "${GEMMA_COMPOSE}")" up -d
  wait_ready 120
}

start_qwen_35b_a3b() {
  cd "$(dirname "${QWEN35BA3B_COMPOSE}")"
  MODEL_DIR="${MODEL_DIR}" docker compose -f "$(basename "${QWEN35BA3B_COMPOSE}")" up -d
  wait_ready 180
}

status() {
  local names
  names=$(llm_containers)
  if [[ -z "${names}" ]]; then
    echo "  (no LLM profile up)"
  else
    while IFS= read -r n; do
      docker ps --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=^${n}$"
    done <<< "${names}"
  fi
  echo "VRAM: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader)"
  echo "Endpoint: ${ENDPOINT}"
  curl -sf "${ENDPOINT}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(\"  served model:\", d[\"data\"][0][\"id\"])" 2>/dev/null || echo "  (endpoint not responding)"
}

list_profiles() {
  cat <<EOF
Profiles:
  tools-text         Qwen3.6-27B int4 + fp8 KV + MTP n=3, 75K ctx
                     Decode: 71 narr / 91 code TPS. Prefill 1042-1194 PP TPS.
                     Use for tool-calling sessions at or under 75K.
  llamacpp-qwen      Qwen3.6-27B Q3_K_XL + q4_0 KV, 262K ctx, vision on
                     Decode: 37 TPS flat.
                     Use for long context and vision when MTP's 131K cap is too small.
  llamacpp-qwen-mtp  Qwen3.6-27B Q3_K_XL + MTP n=2, 131K ctx, vision on
                     Decode: 48.7 TPS. Draft acceptance about 80% when warm.
                     Use for agent work at or under 131K.
  gemma              Gemma-4-26B-A4B Q4_K_XL + ngram-mod, 262K ctx
                     Decode: 131 narr / 138 code TPS.
                     Use when long-context speed matters more than dense quality.
  qwen-35b-a3b       Qwen3.6-35B-A3B UD-Q4_K_XL + q4_0 KV, 262K ctx
                     Decode: 138 / 138 TPS. Spec-decode off.
                     Use as the fast long-context default.
EOF
}

case "${1:-status}" in
  status)         status ;;
  list)           list_profiles ;;
  stop)           stop_all ;;
  tools-text)         stop_all; start_tools_text ;;
  llamacpp-qwen)      stop_all; start_llamacpp_qwen ;;
  llamacpp-qwen-mtp)  stop_all; start_llamacpp_qwen_mtp ;;
  gemma)              stop_all; start_gemma ;;
  qwen-35b-a3b)       stop_all; start_qwen_35b_a3b ;;
  *)
    echo "unknown profile: ${1}"
    echo
    list_profiles
    exit 1
    ;;
esac
