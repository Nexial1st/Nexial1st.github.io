#!/usr/bin/env python3
"""Encrypt HTML pages behind a password (AES-256-GCM, PBKDF2-SHA256).

Each target file is replaced in-place by a small login page carrying the
encrypted original. The correct password decrypts and renders it in the
browser via WebCrypto; without it the content is unreadable.

Usage:
    python3 tools/protect.py 'your-password' file1.html file2.html ...

Keep unencrypted master copies of your maps somewhere private (e.g. on
your own computer) — to update a protected page, edit the master copy and
re-run this script on it. Requires: pip install cryptography
"""
import base64, re, secrets, sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256

ITERATIONS = 600_000
# One salt shared across pages so the browser can cache the derived key
# for the whole site (the password is shared anyway).
SALT = base64.b64decode("RW56eW1lQ29uc3VsdDE=")

FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
           "<path d='M18 20L46 16M18 20L38 46M46 16L38 46' stroke='%231E3D31' stroke-width='4' fill='none'/>"
           "<circle cx='18' cy='20' r='10' fill='%232E5946'/>"
           "<circle cx='46' cy='16' r='7' fill='%23C9683C'/>"
           "<circle cx='38' cy='46' r='9' fill='%2375885F'/></svg>")

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
  <svg width="38" height="38" viewBox="0 0 64 64" aria-hidden="true"><path d="M18 20L46 16M18 20L38 46M46 16L38 46" stroke="#1E3D31" stroke-width="4" fill="none"/><circle cx="18" cy="20" r="10" fill="#2E5946"/><circle cx="46" cy="16" r="7" fill="#C9683C"/><circle cx="38" cy="46" r="9" fill="#75885F"/></svg>
  <div class="brand">Enzyme Consulting</div>
  <div class="sub">Protected Map</div>
  <h1>{title}</h1>
  <p class="hint">This map is password-protected. Enter the access password to view it.</p>
  <input type="password" id="pw" placeholder="Password" autocomplete="current-password" autofocus>
  <button type="submit" id="btn">Unlock</button>
  <div class="err" id="err"></div>
  <div class="foot"><a href="/">&larr; All maps</a> &middot; Access: <a href="mailto:andrew@enzyme.consulting">andrew@enzyme.consulting</a></div>
</form>
<script>
const P={{salt:"{salt}",iv:"{iv}",iters:{iters},data:"{data}"}};
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const KEYSTORE="ec_k";
async function decryptWith(key){{
  const pt=await crypto.subtle.decrypt({{name:"AES-GCM",iv:b64(P.iv)}},key,b64(P.data));
  return new TextDecoder().decode(pt);
}}
function render(html){{document.open();document.write(html);document.close();}}
async function unlock(pw){{
  const km=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
  const key=await crypto.subtle.deriveKey({{name:"PBKDF2",salt:b64(P.salt),iterations:P.iters,hash:"SHA-256"}},km,{{name:"AES-GCM",length:256}},true,["decrypt"]);
  const html=await decryptWith(key);
  try{{
    const raw=await crypto.subtle.exportKey("raw",key);
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
    const key=await crypto.subtle.importKey("raw",b64(k),{{name:"AES-GCM"}},false,["decrypt"]);
    render(await decryptWith(key));
  }}catch(e){{sessionStorage.removeItem(KEYSTORE);}}
}}
// document.open() is silently ignored while the parser is still active,
// so wait for the document to finish loading before auto-unlocking.
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",autoUnlock);
else autoUnlock();
</script>
</body>
</html>
"""

def protect(path: Path, password: str) -> None:
    html = path.read_text()
    if 'const P={"salt"' in html or "ec_k" in html:
        print(f"skip (already protected): {path.name}")
        return
    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title_m.group(1).strip() if title_m else path.stem
    # carry over description/og meta so shared links still preview nicely
    meta = "".join(m.group(0) + "\n" for m in re.finditer(
        r'<meta (?:name="description"|property="og:[a-z_:]+"|name="twitter:card")[^>]*>', html))
    kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=SALT, iterations=ITERATIONS)
    key = kdf.derive(password.encode())
    iv = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(iv, html.encode(), None)
    shell = SHELL.format(
        title=title, meta=meta, favicon=FAVICON,
        salt=base64.b64encode(SALT).decode(), iv=base64.b64encode(iv).decode(),
        iters=ITERATIONS, data=base64.b64encode(ct).decode())
    path.write_text(shell)
    print(f"protected: {path.name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    for f in sys.argv[2:]:
        protect(Path(f), sys.argv[1])
