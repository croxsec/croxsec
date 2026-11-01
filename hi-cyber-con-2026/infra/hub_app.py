#!/usr/bin/env python3
"""
CROX SWARM HUB — dashboard + API del enjambre.
FastAPI + SQLite. Sirve UI estática + API JSON.

Arranque:  python3 app.py            (lee SWARM_HUB_* env o defaults)
Autenticación humana: usuario/clave en tabla users (PBKDF2).
Autenticación de nodos: header X-Node-Key.
"""
import json, os, sqlite3, time, hashlib, hmac, secrets
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

BASE = Path(__file__).parent
DB = os.environ.get("SWARM_DB", "/var/lib/swarm/hub.db")
STATIC = BASE / "static"
SESSIONS = {}  # token -> (user, expira)
SESSION_TTL = 12 * 3600
NODE_KEYS = {}  # node_id -> key (cargado de SWARM_NODE_KEYS file o env)

def load_node_keys():
    """SWARM_NODE_KEYS='vps-main:clave1,laptop:clave2' o fichero /etc/swarm/node_keys.env"""
    global NODE_KEYS
    raw = os.environ.get("SWARM_NODE_KEYS", "")
    f = os.environ.get("SWARM_NODE_KEYS_FILE", "/etc/swarm/node_keys.env")
    if Path(f).exists():
        for line in Path(f).read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                NODE_KEYS[k.strip()] = v.strip().strip('"').strip("'")
    for pair in raw.split(","):
        if ":" in pair:
            k, v = pair.split(":", 1)
            NODE_KEYS[k.strip()] = v.strip()

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      user TEXT PRIMARY KEY, salt TEXT, hash TEXT, created REAL);
    CREATE TABLE IF NOT EXISTS heartbeats(
      id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, ts REAL, payload TEXT);
    CREATE INDEX IF NOT EXISTS idx_hb_node ON heartbeats(node_id, ts);
    CREATE TABLE IF NOT EXISTS messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT, frm TEXT, to_node TEXT,
      body TEXT, ts REAL, delivered INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS tasks(
      id TEXT PRIMARY KEY, node_id TEXT, title TEXT, state TEXT,
      owner TEXT, progress TEXT, ts REAL);
    """)
    con.commit(); con.close()

def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 100_000)
    return salt, h.hex()

def check_pw(user, pw):
    con = db(); r = con.execute("SELECT salt,hash FROM users WHERE user=?", (user,)).fetchone(); con.close()
    if not r: return False
    return hmac.compare_digest(r["hash"], hash_pw(pw, r["salt"])[1])

def human_auth(req: Request):
    tok = req.cookies.get("swarm_session")
    if tok and tok in SESSIONS and SESSIONS[tok][1] > time.time():
        return SESSIONS[tok][0]
    raise HTTPException(401, "no autenticado")

def node_auth(x_node_key: str = Header(default=""), x_node_id: str = Header(default="")):
    if not x_node_id or NODE_KEYS.get(x_node_id) != x_node_key:
        raise HTTPException(401, "node key inválida")
    return x_node_id

app = FastAPI(title="CROX SWARM", docs_url=None, redoc_url=None)

@app.post("/api/login")
async def login(req: Request):
    b = await req.json()
    u, p = b.get("user", ""), b.get("pass", "")
    if check_pw(u, p):
        tok = secrets.token_urlsafe(32)
        SESSIONS[tok] = (u, time.time() + SESSION_TTL)
        r = JSONResponse({"ok": True, "user": u})
        r.set_cookie("swarm_session", tok, max_age=SESSION_TTL, httponly=True)
        return r
    raise HTTPException(401, "credenciales inválidas")

@app.get("/api/nodes")
async def nodes(user: str = Depends(human_auth)):
    con = db()
    rows = con.execute("""
      SELECT h.node_id, h.ts, h.payload FROM heartbeats h
      JOIN (SELECT node_id, MAX(ts) m FROM heartbeats GROUP BY node_id) t
        ON h.node_id=t.node_id AND h.ts=t.m""").fetchall()
    con.close()
    out = []
    for r in rows:
        p = json.loads(r["payload"])
        p["last_seen"] = r["ts"]
        p["stale"] = (time.time() - r["ts"]) > 90
        out.append(p)
    return sorted(out, key=lambda x: x.get("node_id", ""))

@app.get("/api/nodes/{nid}")
async def node_detail(nid: str, user: str = Depends(human_auth)):
    con = db()
    rows = con.execute("SELECT ts,payload FROM heartbeats WHERE node_id=? ORDER BY ts DESC LIMIT 60", (nid,)).fetchall()
    msgs = con.execute("SELECT * FROM messages WHERE to_node=? AND delivered=0 ORDER BY ts", (nid,)).fetchall()
    con.close()
    return {"history": [{"ts": r["ts"], **json.loads(r["payload"])} for r in rows],
            "pending_messages": [dict(m) for m in msgs]}

@app.post("/api/heartbeat")
async def heartbeat(req: Request, nid: str = Depends(node_auth)):
    b = await req.json()
    b["node_id"] = nid
    ts = time.time()
    con = db()
    con.execute("INSERT INTO heartbeats(node_id,ts,payload) VALUES(?,?,?)",
                (nid, ts, json.dumps(b)))
    for t in b.get("tasks", []):
        con.execute("INSERT OR REPLACE INTO tasks(id,node_id,title,state,owner,progress,ts) VALUES(?,?,?,?,?,?,?)",
                    (t.get("id", f"{nid}-{ts}"), nid, t.get("title", ""), t.get("state", "active"),
                     t.get("owner", nid), t.get("progress", ""), ts))
    msgs = con.execute("SELECT id,frm,body,ts FROM messages WHERE to_node=? AND delivered=0 ORDER BY ts LIMIT 20", (nid,)).fetchall()
    if msgs:
        con.executemany("UPDATE messages SET delivered=1 WHERE id=?", [(m["id"],) for m in msgs])
    con.commit(); con.close()
    # purga histórico > 48h
    con = db(); con.execute("DELETE FROM heartbeats WHERE ts < ?", (ts - 48*3600,)); con.commit(); con.close()
    return {"ok": True, "ts": ts, "messages": [dict(m) for m in msgs]}

@app.post("/api/message")
async def post_message(req: Request, user=Depends(human_auth)):
    b = await req.json()
    con = db()
    con.execute("INSERT INTO messages(frm,to_node,body,ts) VALUES(?,?,?,?)",
                (b.get("from", user), b["to"], b["body"], time.time()))
    con.commit(); con.close()
    return {"ok": True}

@app.get("/api/messages")
async def list_messages(limit: int = 30, user=Depends(human_auth)):
    con = db()
    msgs = con.execute('SELECT frm AS "from", to_node AS "to", body, ts FROM messages ORDER BY ts DESC LIMIT ?', (min(limit,200),)).fetchall()
    con.close()
    return [dict(m) for m in msgs]

@app.get("/api/tasks")
async def tasks(user: str = Depends(human_auth)):
    con = db()
    rows = con.execute("SELECT * FROM tasks ORDER BY ts DESC LIMIT 100").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.post("/api/tasks/{tid}/claim")
async def claim(tid: str, req: Request, user=Depends(human_auth)):
    b = await req.json(); con = db()
    con.execute("UPDATE tasks SET owner=? WHERE id=?", (b.get("owner", user), tid))
    con.commit(); con.close()
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC / "index.html").read_text()

@app.post("/api/admin/user")
async def add_user(req: Request, user=Depends(human_auth)):
    b = await req.json()
    if b.get("admin_token") != os.environ.get("SWARM_ADMIN_TOKEN", ""):
        raise HTTPException(403)
    s, h = hash_pw(b["pass"])
    con = db(); con.execute("INSERT OR REPLACE INTO users(user,salt,hash,created) VALUES(?,?,?,?)",
                            (b["user"], s, h, time.time()))
    con.commit(); con.close()
    return {"ok": True}

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

if __name__ == "__main__":
    init(); load_node_keys()
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("SWARM_PORT", "8787")), log_level="warning")
