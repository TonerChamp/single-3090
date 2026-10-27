import json, urllib.request, time

needle = "The secret code is MAGENTA-OWL-7."
# ~100K tokens worth of filler
filler = " The quick brown fox jumps over the lazy dog." * 13500
content = filler[:len(filler)//2] + " " + needle + " " + filler[len(filler)//2:] + "\n\nWhat is the secret code? Respond with just the code."

body = {
    "model": "qwen3.6-35b-a3b-gguf",
    "messages": [{"role": "user", "content": content}],
    "max_tokens": 32,
    "temperature": 0,
    "stream": False,
}
req = urllib.request.Request(
    "http://localhost:8020/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"content-type": "application/json"},
)
t0 = time.time()
resp = json.loads(urllib.request.urlopen(req, timeout=900).read())
wall = time.time() - t0
u = resp["usage"]
out = resp["choices"][0]["message"]["content"]
found = "MAGENTA-OWL-7" in out
ptok = u["prompt_tokens"]
print(f"100K needle: wall={wall:.1f}s in={ptok} out_chars={len(out)} found={found}")
print(f"   pp_tps={ptok/wall:.0f}")
print(f"   answer: {out[:80]!r}")
