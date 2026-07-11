#!/usr/bin/env python3
"""Encrypt HTML pages behind one or more passwords (AES-256-GCM, PBKDF2).

Each target file is replaced in-place by a small login page carrying the
encrypted original. Any of the listed passwords decrypts and renders it in
the browser via WebCrypto; without one the content is unreadable.

Usage:
    python3 tools/protect.py 'password' file1.html file2.html ...
    python3 tools/protect.py 'master-pw,client-pw' client-map.html ...

Comma-separated passwords all unlock the file (envelope encryption: the
page is sealed with a random key, which is wrapped once per password).
Typical use: every file gets the master password plus that client's own
password, so each client only ever unlocks their own maps.

Keep unencrypted master copies of your maps somewhere private (e.g. on
your own computer) — to update a protected page, edit the master copy and
re-run this script on it. Requires: pip install cryptography
"""
import base64, json, re, secrets, sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256

ITERATIONS = 600_000
# One salt shared across pages so the browser can cache the derived key
# for the whole site (the password is shared anyway).
SALT = base64.b64decode("RW56eW1lQ29uc3VsdDE=")

FAVICON = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 280 276'><path fill='%231E3D31' fill-rule='evenodd' d=&quot;M49.8 273.7C48.7 272.6 48 263.8 46.7 236.4C45.7 216.6 44.7 198 44.3 194.8L43.8 189.2L38 187.1C-10.4 169.4 -8.6 98.5 40.4 89.9C71.4 84.6 95.5 117.7 78.1 141.7C69.8 153.2 50.4 154.3 44 143.7C37.3 132.7 45.9 120.6 53.4 130.5C56.6 134.6 58.8 134.9 61.9 131.6C67.4 125.8 64.5 115.7 56.1 111.3C40.1 102.9 20.4 119 22.3 139.1C24.8 166.5 57.9 180.1 82.9 164C100.8 152.4 105.7 134.1 98.5 105.5C94.1 87.8 93.9 74.3 97.8 64.2L99.8 58.9L97.7 57.6C92.5 54.4 59.7 38.1 59.1 38.4C58.7 38.7 59 48 59.6 59.2C60.3 70.3 60.5 79.8 60.1 80.2C59.8 80.6 57.7 80.5 55.5 80C53.3 79.5 48.5 79 44.8 79L38 79L37.9 73.2C37.9 70.1 37.1 53.3 36.1 36C34.6 10 34.6 4.2 35.6 3.1C36.8 1.8 41.7 4 70.2 18.5C88.5 27.7 105.3 36.4 107.6 37.6L111.7 40L117.4 35.5C153.6 7.5 205.1 30.4 202.8 73.5C201.2 104.9 165.7 122.9 144 103.4C126.8 87.9 136.5 57.5 156.8 63C165.8 65.4 168.3 77 159.8 77C152.8 77 150.8 82.2 155.6 87.9C164.9 99 183 87.6 183 70.7C183 45.3 149.4 33.8 128.5 52.1C111.7 66.8 110.1 94.6 125.1 111.4C131.2 118.3 139.9 123.6 150 126.6C170.9 132.8 175.5 134.5 181.2 138.2C184.5 140.3 189.6 144.6 192.5 147.7C196.1 151.4 198.3 153 199.2 152.5C207.7 147.7 235.8 128.5 235.4 127.8C235.1 127.3 226.8 122.9 216.9 118C207.1 113 199 108.7 199 108.3C199 108 200.8 105.4 203 102.5C205.1 99.7 207.6 95.7 208.5 93.6C209.4 91.6 210.4 90 210.9 90.2C211.3 90.4 226.6 98.1 244.9 107.4C273.2 121.7 278.1 124.5 277.8 126.2C277.6 127.6 267.2 134.9 243 150.7C209 172.8 208.5 173.1 208.7 176.3C209.9 195.7 208.9 203.1 203.7 213.8C194 233.9 170.2 246.3 149.5 242C116.5 235.2 102.7 196.6 126 175.7C139.7 163.3 161.2 166.2 168.1 181.4C173.8 193.9 163.4 208.6 152.9 203C150.9 201.9 150.2 196.6 152 195.5C152.6 195.2 153 193.6 153 192.1C153 183.8 140.2 185.3 135.8 194.1C126.7 211.8 151.3 230 170.8 220.1C198.3 206.1 194.5 165.9 164.4 151.8C146.3 143.3 129.3 148.1 109.2 167.3C94 181.9 85.3 187 71.5 189.8L67.5 190.6L67.8 209.1C68 219.3 68.4 229.7 68.8 232.3L69.5 236.9L87 225.5C96.6 219.2 104.8 214 105.1 214C105.4 214 106.2 215.7 106.8 217.8C107.4 219.8 109.5 224.2 111.5 227.4C113.5 230.7 114.7 233.7 114.3 234.1C113.5 234.8 61.2 268.9 54.8 272.8C51.7 274.7 51 274.8 49.8 273.7Z&quot;/></svg>"

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="noindex">
{meta}<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400&family=Inter:wght@300;400;600&family=DM+Mono:wght@400&display=swap">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',Arial,sans-serif;background:#EFE9DD;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}}
.card{{background:#FAF7F0;border:1px solid #D9D1C1;padding:48px 40px 36px;max-width:420px;width:100%;text-align:center}}
.brand{{font-family:'Fraunces',Georgia,serif;font-size:19px;font-weight:500;color:#141F1A;margin:14px 0 4px}}
.sub{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.28em;text-transform:uppercase;color:#C9683C;margin-bottom:26px}}
h1{{font-family:'Fraunces',Georgia,serif;font-size:23px;font-weight:500;color:#2E5946;line-height:1.28;margin-bottom:10px;letter-spacing:-.005em}}
.hint{{font-size:12.5px;font-weight:300;color:#4A5450;margin-bottom:26px;line-height:1.7}}
input{{width:100%;font-family:'Inter',Arial,sans-serif;font-size:14px;padding:12px 14px;border:1px solid #D9D1C1;background:#fff;color:#141F1A;outline:none;text-align:center;letter-spacing:.04em}}
input:focus{{border-color:#1E3D31}}
button{{width:100%;margin-top:12px;font-family:'Inter',Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#F6F3EB;background:#1E3D31;border:none;padding:14px;cursor:pointer;transition:background .15s}}
button:hover{{background:#10231C}}
button:disabled{{background:#75885F;cursor:wait}}
.err{{font-size:11.5px;color:#B04A32;margin-top:12px;min-height:16px}}
.foot{{margin-top:22px;font-size:10.5px;font-weight:300;color:#4A5450}}
.foot a{{color:#1E3D31;text-decoration:none;border-bottom:1px solid rgba(30,61,49,.35);padding-bottom:2px}}
</style>
</head>
<body>
<form class="card" id="f">
  <svg width="46" height="45" viewBox="0 0 280 276" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M49.8 273.7C48.7 272.6 48 263.8 46.7 236.4C45.7 216.6 44.7 198 44.3 194.8L43.8 189.2L38 187.1C-10.4 169.4 -8.6 98.5 40.4 89.9C71.4 84.6 95.5 117.7 78.1 141.7C69.8 153.2 50.4 154.3 44 143.7C37.3 132.7 45.9 120.6 53.4 130.5C56.6 134.6 58.8 134.9 61.9 131.6C67.4 125.8 64.5 115.7 56.1 111.3C40.1 102.9 20.4 119 22.3 139.1C24.8 166.5 57.9 180.1 82.9 164C100.8 152.4 105.7 134.1 98.5 105.5C94.1 87.8 93.9 74.3 97.8 64.2L99.8 58.9L97.7 57.6C92.5 54.4 59.7 38.1 59.1 38.4C58.7 38.7 59 48 59.6 59.2C60.3 70.3 60.5 79.8 60.1 80.2C59.8 80.6 57.7 80.5 55.5 80C53.3 79.5 48.5 79 44.8 79L38 79L37.9 73.2C37.9 70.1 37.1 53.3 36.1 36C34.6 10 34.6 4.2 35.6 3.1C36.8 1.8 41.7 4 70.2 18.5C88.5 27.7 105.3 36.4 107.6 37.6L111.7 40L117.4 35.5C153.6 7.5 205.1 30.4 202.8 73.5C201.2 104.9 165.7 122.9 144 103.4C126.8 87.9 136.5 57.5 156.8 63C165.8 65.4 168.3 77 159.8 77C152.8 77 150.8 82.2 155.6 87.9C164.9 99 183 87.6 183 70.7C183 45.3 149.4 33.8 128.5 52.1C111.7 66.8 110.1 94.6 125.1 111.4C131.2 118.3 139.9 123.6 150 126.6C170.9 132.8 175.5 134.5 181.2 138.2C184.5 140.3 189.6 144.6 192.5 147.7C196.1 151.4 198.3 153 199.2 152.5C207.7 147.7 235.8 128.5 235.4 127.8C235.1 127.3 226.8 122.9 216.9 118C207.1 113 199 108.7 199 108.3C199 108 200.8 105.4 203 102.5C205.1 99.7 207.6 95.7 208.5 93.6C209.4 91.6 210.4 90 210.9 90.2C211.3 90.4 226.6 98.1 244.9 107.4C273.2 121.7 278.1 124.5 277.8 126.2C277.6 127.6 267.2 134.9 243 150.7C209 172.8 208.5 173.1 208.7 176.3C209.9 195.7 208.9 203.1 203.7 213.8C194 233.9 170.2 246.3 149.5 242C116.5 235.2 102.7 196.6 126 175.7C139.7 163.3 161.2 166.2 168.1 181.4C173.8 193.9 163.4 208.6 152.9 203C150.9 201.9 150.2 196.6 152 195.5C152.6 195.2 153 193.6 153 192.1C153 183.8 140.2 185.3 135.8 194.1C126.7 211.8 151.3 230 170.8 220.1C198.3 206.1 194.5 165.9 164.4 151.8C146.3 143.3 129.3 148.1 109.2 167.3C94 181.9 85.3 187 71.5 189.8L67.5 190.6L67.8 209.1C68 219.3 68.4 229.7 68.8 232.3L69.5 236.9L87 225.5C96.6 219.2 104.8 214 105.1 214C105.4 214 106.2 215.7 106.8 217.8C107.4 219.8 109.5 224.2 111.5 227.4C113.5 230.7 114.7 233.7 114.3 234.1C113.5 234.8 61.2 268.9 54.8 272.8C51.7 274.7 51 274.8 49.8 273.7Z"/></svg>
  <div class="brand">Enzyme Consulting</div>
  <div class="sub">Protected Map</div>
  <h1>{title}</h1>
  <p class="hint">This map is password-protected.<br>Enter the access password to view it.</p>
  <input type="password" id="pw" placeholder="Password" autocomplete="current-password" autofocus>
  <button type="submit" id="btn">Unlock</button>
  <div class="err" id="err"></div>
  <div class="foot"><a href="/">&larr; All maps</a> &middot; Access: <a href="mailto:andrew@enzyme.consulting">andrew@enzyme.consulting</a></div>
</form>
<script>
const P={{salt:"{salt}",iv:"{iv}",iters:{iters},slots:{slots},data:"{data}"}};
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const KEYSTORE="ec_k";
// kek unwraps the random content key from whichever slot it fits; the
// content key then decrypts the page. Any authorized password works.
async function decryptWith(kek){{
  for(const s of P.slots){{
    try{{
      const raw=await crypto.subtle.decrypt({{name:"AES-GCM",iv:b64(s.iv)}},kek,b64(s.k));
      const ck=await crypto.subtle.importKey("raw",raw,{{name:"AES-GCM"}},false,["decrypt"]);
      const pt=await crypto.subtle.decrypt({{name:"AES-GCM",iv:b64(P.iv)}},ck,b64(P.data));
      return new TextDecoder().decode(pt);
    }}catch(e){{}}
  }}
  throw new Error("no matching slot");
}}
function render(html){{document.open();document.write(html);document.close();}}
async function unlock(pw){{
  const km=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
  const kek=await crypto.subtle.deriveKey({{name:"PBKDF2",salt:b64(P.salt),iterations:P.iters,hash:"SHA-256"}},km,{{name:"AES-GCM",length:256}},true,["decrypt"]);
  const html=await decryptWith(kek);
  try{{
    const raw=await crypto.subtle.exportKey("raw",kek);
    sessionStorage.setItem(KEYSTORE,btoa(String.fromCharCode(...new Uint8Array(raw))));
  }}catch(e){{}}
  render(html);
}}
document.getElementById("f").addEventListener("submit",async e=>{{
  e.preventDefault();
  const btn=document.getElementById("btn"),err=document.getElementById("err");
  btn.disabled=true;btn.textContent="Unlocking\\u2026";err.textContent="";
  try{{await unlock(document.getElementById("pw").value);}}
  catch(ex){{
    err.textContent="Incorrect password \\u2014 please try again.";
    btn.disabled=false;btn.textContent="Unlock";
    document.getElementById("pw").select();
  }}
}});
async function autoUnlock(){{
  const k=sessionStorage.getItem(KEYSTORE);
  if(!k)return;
  try{{
    const kek=await crypto.subtle.importKey("raw",b64(k),{{name:"AES-GCM"}},false,["decrypt"]);
    render(await decryptWith(kek));
  }}catch(e){{}}
}}
// document.open() is silently ignored while the parser is still active,
// so wait for the document to finish loading before auto-unlocking.
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",autoUnlock);
else autoUnlock();
</script>
</body>
</html>
"""

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()

def protect(path: Path, passwords: list[str]) -> None:
    html = path.read_text()
    if "ec_k" in html:
        print(f"skip (already protected): {path.name}")
        return
    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title_m.group(1).strip() if title_m else path.stem
    # carry over description/og meta so shared links still preview nicely
    meta = "".join(m.group(0) + "\n" for m in re.finditer(
        r'<meta (?:name="description"|property="og:[a-z_:]+"|name="twitter:card")[^>]*>', html))
    # envelope encryption: seal the page with a random content key, then
    # wrap that key once per password so any of them can open the page
    content_key = secrets.token_bytes(32)
    iv = secrets.token_bytes(12)
    ct = AESGCM(content_key).encrypt(iv, html.encode(), None)
    slots = []
    for pw in passwords:
        kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=SALT, iterations=ITERATIONS)
        kek = kdf.derive(pw.encode())
        siv = secrets.token_bytes(12)
        slots.append({"iv": b64(siv), "k": b64(AESGCM(kek).encrypt(siv, content_key, None))})
    shell = SHELL.format(
        title=title, meta=meta, favicon=FAVICON,
        salt=b64(SALT), iv=b64(iv), iters=ITERATIONS,
        slots=json.dumps(slots, separators=(",", ":")), data=b64(ct))
    path.write_text(shell)
    print(f"protected ({len(slots)} password{'s' if len(slots) > 1 else ''}): {path.name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pws = [p for p in sys.argv[1].split(",") if p]
    for f in sys.argv[2:]:
        protect(Path(f), pws)
