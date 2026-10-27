#!/usr/bin/env python3
"""
llm-proxy.py — sentinel-aware reverse proxy for the local LLM endpoint.

Listens on :8000. Forwards to http://127.0.0.1:8020 (the LLM container).
If /tmp/llm-switch.lock exists, returns 503 immediately so a client in
front of this proxy can fail over for the duration of the swap.

swap/llm-switch.sh touches the sentinel before stopping a profile and
removes it after the new profile passes its health check.
"""
from __future__ import annotations
import asyncio, os, sys
from aiohttp import web, ClientSession, ClientTimeout

UPSTREAM = "http://127.0.0.1:8020"
LOCK = "/tmp/llm-switch.lock"
LISTEN_PORT = 8000

session: ClientSession | None = None

async def on_startup(app):
    global session
    # 30-min request timeout — long-ctx generations are slow.
    session = ClientSession(timeout=ClientTimeout(total=1800, connect=5))

async def on_cleanup(app):
    await session.close()

async def health(request: web.Request) -> web.Response:
    if os.path.exists(LOCK):
        return web.json_response(
            {"status": "swapping", "lock": LOCK},
            status=503,
        )
    try:
        async with session.get(f"{UPSTREAM}/v1/models", timeout=ClientTimeout(total=3)) as r:
            return web.json_response(
                {"status": "ok" if r.status == 200 else "upstream_error", "upstream_status": r.status},
                status=200 if r.status == 200 else 503,
            )
    except Exception as e:
        return web.json_response({"status": "upstream_unreachable", "error": str(e)}, status=503)

async def proxy(request: web.Request) -> web.StreamResponse:
    if os.path.exists(LOCK):
        return web.json_response(
            {"error": {"message": "local LLM profile is swapping; retry shortly or use another endpoint", "type": "service_unavailable"}},
            status=503,
        )

    url = f"{UPSTREAM}{request.path_qs}"
    # Strip hop-by-hop + host headers.
    drop = {"host", "content-length", "transfer-encoding", "connection"}
    headers = {k: v for k, v in request.headers.items() if k.lower() not in drop}

    body = await request.read() if request.body_exists else None

    try:
        async with session.request(
            request.method, url, headers=headers, data=body, allow_redirects=False
        ) as upstream:
            resp = web.StreamResponse(status=upstream.status, headers={
                k: v for k, v in upstream.headers.items()
                if k.lower() not in {"transfer-encoding", "content-encoding", "content-length"}
            })
            await resp.prepare(request)
            async for chunk in upstream.content.iter_any():
                await resp.write(chunk)
            await resp.write_eof()
            return resp
    except Exception as e:
        return web.json_response(
            {"error": {"message": f"upstream error: {e}", "type": "bad_gateway"}},
            status=502,
        )

def make_app() -> web.Application:
    app = web.Application(client_max_size=512 * 1024 * 1024)  # 512 MB for big prompts
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/healthz", health)
    app.router.add_route("*", "/{path:.*}", proxy)
    return app

if __name__ == "__main__":
    web.run_app(make_app(), host="0.0.0.0", port=LISTEN_PORT, access_log=None)
