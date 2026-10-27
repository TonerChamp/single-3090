#!/usr/bin/env python3
"""HTTP wrapper around swap/llm-switch.sh. A client swaps the active local
profile without a shell on the rig.

Endpoints:
  GET  /current     -> {"profile": "llamacpp-qwen-mtp" | "qwen-35b-a3b" | ...}
  POST /switch      -> body {"profile": "<name>"}, returns when /v1/models ready
                       {"ok": true, "profile": "<name>", "elapsed_ms": 18000, "noop": false}
                       Idempotent: no-op if already on that profile.
  GET  /healthz     -> 200 OK if API alive

Auth: shared bearer token in SWITCH_TOKEN env var. Reject without it.
"""
import os, json, time, subprocess, asyncio
from aiohttp import web

TOKEN = os.environ["SWITCH_TOKEN"]  # crash if unset
SWITCH = os.path.expanduser("~/single-3090/swap/llm-switch.sh")
ENDPOINT = "http://localhost:8020/v1/models"
PROFILE_BY_CONTAINER = {
    "llama-cpp-qwen36-27b":         "llamacpp-qwen",
    "llama-cpp-qwen36-27b-mtp":     "llamacpp-qwen-mtp",
    "llamacpp-gemma4-26b-a4b":      "gemma",
    "llamacpp-qwen36-35b-a3b":      "qwen-35b-a3b",
    "vllm-qwen36-27b-tools-text":   "tools-text",
}

def current_profile() -> str | None:
    out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], text=True)
    for name in out.strip().splitlines():
        if name in PROFILE_BY_CONTAINER:
            return PROFILE_BY_CONTAINER[name]
    return None

def auth(req) -> bool:
    h = req.headers.get("authorization", "")
    return h == f"Bearer {TOKEN}"

async def healthz(req): return web.Response(text="ok")

async def current(req):
    if not auth(req): return web.Response(status=401)
    return web.json_response({"profile": current_profile()})

async def switch(req):
    if not auth(req): return web.Response(status=401)
    body = await req.json()
    target = body.get("profile")
    if target not in {"llamacpp-qwen", "llamacpp-qwen-mtp", "gemma", "qwen-35b-a3b", "tools-text"}:
        return web.json_response({"ok": False, "error": "unknown profile"}, status=400)
    cur = current_profile()
    if cur == target:
        return web.json_response({"ok": True, "profile": target, "elapsed_ms": 0, "noop": True})
    t0 = time.time()
    proc = await asyncio.create_subprocess_exec(
        "bash", SWITCH, target,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await proc.communicate()
    elapsed = int((time.time() - t0) * 1000)
    if proc.returncode != 0:
        return web.json_response({"ok": False, "elapsed_ms": elapsed,
                                  "log": stdout.decode()[-2000:]}, status=500)
    return web.json_response({"ok": True, "profile": target, "elapsed_ms": elapsed, "noop": False})

app = web.Application()
app.router.add_get("/healthz", healthz)
app.router.add_get("/current", current)
app.router.add_post("/switch", switch)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=9090)
