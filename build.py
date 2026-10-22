#!/usr/bin/env python3
# 抓取 sources.txt 里的 Surge 模块，合并成一个 sgmodule，并更新 gist。
import os, re, sys, json, urllib.request

GIST_ID = os.environ.get("GIST_ID", "")
TOKEN   = os.environ.get("GIST_TOKEN", "")
FILENAME= "EgernSync.sgmodule"
UA = {"User-Agent": "Mozilla/5.0 (compatible; surge-bundle/1.0)"}

def get(url):
    from urllib.parse import quote
    url = quote(url, safe=":/?&=#%+@!$'()*;,[]~")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def parse_args(s):
    out = {}; i = 0; n = len(s)
    while i < n:
        j = s.find(":", i)
        if j < 0: break
        name = s[i:j].strip().strip("=")
        i = j + 1
        while i < n and s[i] == " ": i += 1
        if i < n and s[i] == '"':
            i += 1; val = ""
            while i < n and s[i] != '"': val += s[i]; i += 1
            i += 1
            while i < n and s[i] in ", ": i += 1
        else:
            k = s.find(",", i)
            if k < 0: val = s[i:]; i = n
            else: val = s[i:k]; i = k + 1
        out[name] = val
    return out

def parse_sections(text):
    out = {}; cur = None
    for line in text.split("\n"):
        m = re.match(r"^\[(.+?)\]\s*$", line.strip())
        if m:
            cur = m.group(1).strip(); out.setdefault(cur, []); continue
        if cur is not None:
            out[cur].append(line)
    return out

def build(urls):
    merged = {"Script": []}; scripts = {}; hosts = []; seenh = set(); seen = set(); failed = []
    for u in urls:
        u = u.strip()
        if not u or u.startswith("#"): continue
        try:
            body = get(u)
        except Exception as e:
            failed.append((u, str(e))); continue
        args = {}
        for l in body.split("\n"):
            if re.match(r"^#!arguments\s*=", l):
                args = parse_args(l.split("=", 1)[1])
        body = body.replace("https://kelee.one/Resource/", "https://hub.kelee.one/Resource/")
        for sec, lines in parse_sections(body).items():
            if sec == "General": continue
            for line in lines:
                s = line.rstrip()
                if not s.strip(): continue
                for k, v in args.items():
                    s = s.replace("{{{" + k + "}}}", v)
                if "{{{" in s: continue
                if s.strip().startswith("#"): continue
                if sec == "MITM":
                    if s.strip().lower().startswith("hostname"):
                        for h in [x.strip() for x in s.split("=", 1)[1].replace("%APPEND%", "").split(",") if x.strip()]:
                            if h not in seenh: seenh.add(h); hosts.append(h)
                    continue
                if sec == "Script":
                    k, _, rest = s.partition("="); k = k.strip(); base = k
                    while k in scripts: k = f"{base}·{len(scripts)}"
                    scripts[k] = rest.strip(); continue
                key = (sec, s)
                if key in seen: continue
                seen.add(key); merged.setdefault(sec, []).append(s)
    merged["Script"] = [f"{k} = {v}" for k, v in scripts.items()]
    out = ["#!name=Egern 同步包",
           "#!desc=由 sources.txt 里的模块自动合并生成；参数按各模块默认值固化。",
           "#!author=liuweiqiang0523", ""]
    for sec in ["Script", "URL Rewrite", "Header Rewrite", "Body Rewrite", "Map Local", "Rule"]:
        if merged.get(sec): out += [f"[{sec}]"] + merged[sec] + [""]
    out += ["[MITM]", "hostname = %APPEND% " + ", ".join(hosts)]
    return "\n".join(out) + "\n", failed, len(scripts), len(hosts), len(merged.get("Rule", []))

def main():
    urls = [l for l in open("sources.txt", encoding="utf-8").read().split("\n") if l.strip()]
    content, failed, n_scripts, n_hosts, n_rules = build(urls)
    open(FILENAME, "w", encoding="utf-8").write(content)
    print(f"built: {len(content)} bytes, scripts={n_scripts}, hosts={n_hosts}, rules={n_rules}")
    for u, e in failed:
        print("FAILED:", u, e)
    return 0

if __name__ == "__main__":
    sys.exit(main())
