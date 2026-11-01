#!/usr/bin/env python3
"""
CROX SWARM NODE — agente de nodo.
Recolecta estado local (sistema, procesos OpenClaw, tareas CTF) y hace
heartbeat al hub cada INTERVALO segundos. Recibe mensajes del hub.

Config: /etc/swarm/node.env
  SWARM_NODE_ID=vps-main
  SWARM_NODE_KEY=<secreto>
  SWARM_HUB_URL=https://hub.ejemplo.com   (o http://IP:puerto)
Opcional: SWARM_CTF_TOKEN / SWARM_CTF_API para reportar score.
"""
import json, os, platform, time, subprocess, sys
from pathlib import Path
from urllib import request

ENV = Path("/etc/swarm/node.env")
CFG = {}
if ENV.exists():
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            CFG[k.strip()] = v.strip().strip('"').strip("'")
CFG.update({k[6:]: v for k, v in os.environ.items() if k.startswith("SWARM_")})

NODE_ID = CFG.get("NODE_ID", platform.node())
KEY = CFG.get("NODE_KEY", "")
HUB = CFG.get("HUB_URL", "http://127.0.0.1:8787").rstrip("/")
INTERVAL = int(CFG.get("INTERVAL", "30"))
CTF_TOKEN = CFG.get("CTF_TOKEN", "")
CTF_API = CFG.get("CTF_API", "")
VERSION = "0.1.0"
TASKS_DIR = Path(CFG.get("TASKS_DIR", "/var/lib/swarm/tasks"))

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8).stdout
    except Exception:
        return ""

def sysinfo():
    load = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)
    mem_free = 0
    for l in sh("free -m").splitlines():
        if l.startswith("Mem:"):
            mem_free = int(l.split()[-1]) if l.split()[-1].isdigit() else int(l.split()[3])
    disk_free = 0
    for l in sh("df -BG /").splitlines()[1:]:
        p = l.split()
        disk_free = int(p[3].rstrip("G")) if p[3][0].isdigit() else 0
    return {"load": [round(x, 2) for x in load], "mem_free_mb": mem_free, "disk_free_gb": disk_free}

def openclaw_agents():
    """Subagentes vivos = procesos node del gateway con contexto de subagente,
    más tareas de /tmp conocidas del CTF. Heurística simple y robusta."""
    agents = [{"name": "openclaw-gateway", "kind": "gateway", "status": "running",
               "task": "orquestación principal"}]
    ps = sh("ps aux | grep -E 'subagent|openclaw' | grep -v grep")
    n = len([l for l in ps.splitlines() if l.strip()])
    if n:
        agents.append({"name": "openclaw-workers", "kind": "pool", "status": "running",
                       "task": f"{n} procesos activos"})
    return agents

def ctf_tasks():
    """Lee kills del CTF si hay logs locales."""
    tasks, score, rank = [], None, None
    try:
        import glob
        kills = set()
        for f in glob.glob("/tmp/ctf_solves_*.log"):
            for line in open(f, errors="replace"):
                if line.startswith("SOLVE|"):
                    kills.add(line.split("|")[1].strip())
        if kills:
            score, rank = ctf_score()
            tasks.append({"id": "ctf-campaign", "title": "HI Cyber Con 2026",
                          "state": "active", "owner": NODE_ID,
                          "progress": f"{len(kills)} kills" + (f" · {score}pts" if score else "")})
    except Exception:
        pass
    return tasks, score, rank

def ctf_score():
    if not (CTF_TOKEN and CTF_API):
        return None, None
    try:
        req = request.Request(f"{CTF_API}/api/v1/users/me",
                              headers={"Authorization": f"Bearer {CTF_TOKEN}", "User-Agent": "curl/8.0"})
        d = json.loads(request.urlopen(req, timeout=10).read())
        data = d.get("data", {})
        return data.get("score"), data.get("divisionPlace")
    except Exception:
        return None, None

def local_tasks():
    """Tareas declaradas localmente por cualquier agente (/var/lib/swarm/tasks/*.json)."""
    out = []
    if TASKS_DIR.exists():
        for f in TASKS_DIR.glob("*.json"):
            try:
                out.append(json.loads(f.read_text()))
            except Exception:
                pass
    return out

def heartbeat():
    tasks, score, rank = ctf_tasks()
    tasks += local_tasks()
    extra = {}
    if score is not None:
        extra["ctf_score"] = score
        extra["ctf_rank_div"] = rank
    payload = {"node_id": NODE_ID, "ts": time.time(), "version": VERSION,
               "system": sysinfo(), "agents": openclaw_agents(),
               "tasks": tasks, "extra": extra}
    body = json.dumps(payload).encode()
    req = request.Request(f"{HUB}/api/heartbeat", data=body, method="POST",
                          headers={"Content-Type": "application/json", "X-Node-Id": NODE_ID,
                                   "X-Node-Key": KEY})
    try:
        r = json.loads(request.urlopen(req, timeout=15).read())
        for m in r.get("messages", []):
            print(f"📨 MSG de {m.get('frm')}: {m.get('body')}", flush=True)
        return True
    except Exception as e:
        print(f"⚠ heartbeat falló: {e}", flush=True)
        return False

if __name__ == "__main__":
    if not KEY:
        sys.exit("Falta SWARM_NODE_KEY en /etc/swarm/node.env")
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"🐝 {NODE_ID} → {HUB} cada {INTERVAL}s", flush=True)
    while True:
        heartbeat()
        time.sleep(INTERVAL)
