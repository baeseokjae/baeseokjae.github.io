#!/usr/bin/env python3
"""Ensure Blog Paperclip agents use the hermes_local adapter.

This is run by paperclip.service ExecStartPost and can also be run manually.
It preserves each agent's instruction paths/env, only changing adapter/model/timeout
and the intended heartbeat policy.
"""
import json
import time
import urllib.error
import urllib.request

COMPANY_ID = "52c3998a-6f9c-4454-9ef4-2c2cd574961b"
API = "http://127.0.0.1:3100/api"
HEADERS = {"X-Paperclip-Local-Board": "true", "Content-Type": "application/json"}

TARGETS = {
    "ContentDirector": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": True, "intervalSec": 10800, "maxConcurrentRuns": 1}},
    "Supervisor": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": False, "intervalSec": 86400, "maxConcurrentRuns": 1}},
    "Strategist": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": False}},
    "Researcher": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": False}},
    "writer": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": False}},
    "Analyst": {"model": "deepseek-v4-flash", "heartbeat": {"enabled": False, "intervalSec": 86400, "maxConcurrentRuns": 1}},
    "Publisher": {"model": "ministral-3:8b", "heartbeat": {"enabled": False}},
}


def request(method, path, payload=None, timeout=20):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(API + path, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode() or "null"
        return json.loads(body)


def wait_for_server():
    last = None
    for _ in range(36):  # up to ~3 minutes after Paperclip start
        try:
            return request("GET", f"/companies/{COMPANY_ID}/agents", timeout=10)
        except Exception as exc:  # server still starting / migrations running
            last = exc
            time.sleep(5)
    raise RuntimeError(f"Paperclip API not ready: {last}")


def desired_config(agent, target):
    current = agent.get("adapterConfig") or {}
    # Preserve instruction bundle settings, prompt templates, env, etc.
    # Force the official Hermes Ollama Cloud provider so hermes_local does not
    # inherit the interactive Hermes default provider (openai-codex) and misroute
    # deepseek/ministral. Official provider id: ollama-cloud.
    cfg = {k: v for k, v in current.items() if k not in {"model", "command", "provider"}}
    cfg.update({
        "model": target["model"],
        "provider": "ollama-cloud",
        "timeoutSec": 600,
        "maxTurns": cfg.get("maxTurns", 30),
        "bypassSandbox": True,
        "dangerouslySkipPermissions": True,
        "dangerouslyBypassApprovalsAndSandbox": True,
        "sessionBehavior": cfg.get("sessionBehavior", "new"),
        "persistSession": False,
    })
    return cfg


def main():
    agents = wait_for_server()
    by_name = {a.get("name"): a for a in agents}
    changed = []
    missing = []
    for name, target in TARGETS.items():
        agent = by_name.get(name)
        if not agent:
            missing.append(name)
            continue
        cfg = desired_config(agent, target)
        runtime = dict(agent.get("runtimeConfig") or {})
        runtime["heartbeat"] = target["heartbeat"]
        payload = {
            "adapterType": "hermes_local",
            "adapterConfig": cfg,
            "runtimeConfig": runtime,
            "errorReason": None,
        }
        needs_patch = (
            agent.get("adapterType") != "hermes_local"
            or (agent.get("adapterConfig") or {}).get("model") != target["model"]
            or (agent.get("adapterConfig") or {}).get("provider") != "ollama-cloud"
            or (agent.get("adapterConfig") or {}).get("persistSession") is not False
            or (agent.get("runtimeConfig") or {}).get("heartbeat") != target["heartbeat"]
            or agent.get("errorReason")
        )
        if needs_patch:
            request("PATCH", f"/agents/{agent['id']}", payload, timeout=30)
            changed.append(f"{name}->{target['model']}")
    if changed:
        print("patched: " + ", ".join(changed))
    else:
        print("all target agents already hermes_local")
    if missing:
        print("missing: " + ", ".join(missing))


if __name__ == "__main__":
    main()
