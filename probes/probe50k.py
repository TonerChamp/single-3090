import json, urllib.request, time, sys

body = {
    "model": "qwen3.6-35b-a3b-gguf",
    "messages": [{"role": "user", "content": (" The quick brown fox jumps over the lazy dog." * 6800) + " Summarize in one word."}],
    "max_tokens": 16,
    "temperature": 0,
    "stream": False,
}
req = urllib.request.Request(
    "http://localhost:8020/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"content-type": "application/json"},
)
t0 = time.time()
resp = json.loads(urllib.request.urlopen(req, timeout=600).read())
wall = time.time() - t0
u = resp["usage"]
ptok = u["prompt_tokens"]
ctok = u["completion_tokens"]
pp_tps = ptok / wall
print(f"wall={wall:.1f}s in={ptok} out={ctok} pp_tps={pp_tps:.0f}")
