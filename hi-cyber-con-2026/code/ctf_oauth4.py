#!/usr/bin/env python3
import re, subprocess, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
JAR_CT = "/tmp/ctf_jar.txt"

def gh(args):
    return subprocess.run(["curl", "-s", "-b", "/tmp/gh_j3.txt", "-c", "/tmp/gh_j3.txt", "-A", UA] + args,
                          capture_output=True, text=True).stdout

def ct(args):
    return subprocess.run(["curl", "-s", "-b", JAR_CT, "-c", JAR_CT, "-A", UA] + args,
                          capture_output=True, text=True).stdout

# fresh authorize page
url = open("/tmp/ctf_auth_url.txt").read().strip()
h = gh([url, "--max-time", "40"])
m = re.search(r'<form[^>]*action="/login/oauth/authorize"[^>]*>(.*?)</form>', h, re.S)
if not m:
    print("no form; title:", re.search(r"<title>([^<]+)", h).group(1) if "<title>" in h else "?")
    raise SystemExit(1)
form = m.group(1)
fields = {"authorize": "1"}
for im in re.finditer(r'<input([^>]+)>', form):
    attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', im.group(1)))
    name = attrs.get("name")
    if not name or name == "authorize":
        continue
    fields[name] = attrs.get("value", "")
body = urllib.parse.urlencode(fields)
out = subprocess.run(["curl", "-s", "-b", "/tmp/gh_j3.txt", "-c", "/tmp/gh_j3.txt", "-A", UA,
                      "-H", "Origin: https://github.com", "-H", f"Referer: {url}",
                      "-X", "POST", "https://github.com/login/oauth/authorize", "-d", body,
                      "--max-time", "40", "-D", "/tmp/ctf_auth4_h.txt", "-o", "/dev/null",
                      "--max-redirs", "0"], capture_output=True, text=True)
hd = open("/tmp/ctf_auth4_h.txt").read()
loc = [l.split(": ", 1)[1].strip() for l in hd.splitlines() if l.lower().startswith("location:")]
print("status:", hd.splitlines()[0] if hd else "?", "| loc:", loc[0][:170] if loc else "none")
if loc:
    cb = loc[0]
    # 5) seguir el callback con sesion CTFtime
    r2 = ct([cb, "--max-time", "40", "-D", "/tmp/ctf_cb_h.txt", "-o", "/tmp/ctf_home.html", "-L", "--max-redirs", "5"])
    hd2 = open("/tmp/ctf_cb_h.txt").read()
    home = open("/tmp/ctf_home.html").read()
    logged = "logout" in home.lower() or "Log out" in home or "/logout/" in home
    print("CTFtime home len:", len(home), "| login detectado:", logged)
    m2 = re.search(r'"/team/new"|/profile/|My teams|Create team', home)
    print("marcas:", m2.group(0) if m2 else "?")
    open("/tmp/ctf_logged.html", "w").write(home)
