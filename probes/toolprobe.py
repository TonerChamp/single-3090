import json, urllib.request, time, sys

# OpenAI-compat tools probe. 3 tools, query requires exactly one.
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk and return its contents",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Absolute path to the file"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write contents to a file on disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "contents": {"type": "string"},
                },
                "required": ["path", "contents"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command and return stdout+stderr",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]

queries = [
    ("read", "Please read the contents of the file at /etc/hosts."),
    ("write", "Write 'hello world' to the file /tmp/greeting.txt."),
    ("shell", "Run the shell command `uname -a` and tell me the output."),
    ("read", "I need to see what is in /home/user/notes.md — fetch it for me."),
    ("write", "Create a new file /tmp/log.txt containing the single line 'start'."),
    ("shell", "Run `df -h` to check disk usage on this machine."),
    ("read", "Show me /var/log/syslog."),
    ("write", "Save the text 'config v2' into /opt/app/config.txt please."),
    ("shell", "Execute `nvidia-smi` and report the GPU memory."),
    ("read", "Open /etc/resolv.conf and return its contents."),
]

passes = 0
fails = []
for label, q in queries:
    body = {
        "model": "qwen3.6-35b-a3b-gguf",
        "messages": [{"role": "user", "content": q}],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.8,
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            "http://localhost:8020/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
        msg = resp["choices"][0]["message"]
        tc = msg.get("tool_calls") or []
        if len(tc) == 1:
            name = tc[0]["function"]["name"]
            args_raw = tc[0]["function"]["arguments"]
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                # Pass if name matches expected pattern and args parseable
                expected_map = {"read": "read_file", "write": "write_file", "shell": "run_shell"}
                exp = expected_map[label]
                if name == exp and isinstance(args, dict):
                    passes += 1
                    continue
                fails.append(f"[{label}] wrong tool: got {name} expected {exp}")
            except Exception as e:
                fails.append(f"[{label}] args not parseable: {e}; raw={args_raw[:80]!r}")
        else:
            content = msg.get("content") or ""
            fails.append(f"[{label}] no/multi tool_calls (n={len(tc)}); content head: {content[:120]!r}")
    except Exception as e:
        fails.append(f"[{label}] exception: {e}")

print(f"\nresult: {passes}/{len(queries)} passes")
for f in fails:
    print(f"  FAIL {f}")
