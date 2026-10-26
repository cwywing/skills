#!/usr/bin/env python3
"""App Store Connect API helper (zero-dependency, macOS system python3).

Why this exists: `curl` to api.appstoreconnect.apple.com intermittently
blackholes behind some proxies; python urllib + an ES256 JWT is stable, and the
JWT header must contain ONLY alg/kid (adding typ returns 401).

Config (one of):
  - env:  ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_PATH (or ~/.appstoreconnect layout)
  - asc CLI profile: run `asc auth doctor`; key sits in the system keychain, so
    export it once or point ASC_KEY_PATH at a AuthKey_<KEYID>.p8 file.

Usage:
  python3 asc_api.py METHOD path [json_body_file]
    METHOD: GET | POST | PATCH | DELETE
    path:   /v1/apps?filter[bundleId]=...   (absolute path, BASE prepended)
    body:   path to a JSON file, or "-" for stdin

Exit codes: 0 = 2xx/204, 1 = HTTP error or unreachable (body printed as JSON).
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

BASE = "https://api.appstoreconnect.apple.com"


def _config():
    key_id = os.environ.get("ASC_KEY_ID", "")
    issuer = os.environ.get("ASC_ISSUER_ID", "")
    key_path = os.environ.get("ASC_KEY_PATH", "")
    if not key_path:
        key_path = os.path.expanduser(
            f"~/.appstoreconnect/private_keys/AuthKey_{key_id}.p8")
    if not (key_id and issuer and os.path.exists(key_path)):
        # fall back to any env file in ~/.appstoreconnect/ (export ASC_KEY_ID=…)
        import glob as _glob
        candidates = sorted(_glob.glob(
            os.path.expanduser("~/.appstoreconnect/*.env")))
        env = candidates[0] if candidates else None
        if env:
            for line in open(env):
                if line.startswith("export ASC_KEY_ID="):
                    key_id = key_id or line.split("=", 1)[1].strip()
                elif line.startswith("export ASC_ISSUER_ID="):
                    issuer = issuer or line.split("=", 1)[1].strip()
            if not key_path or not os.path.exists(key_path):
                key_path = os.path.expanduser(
                    f"~/.appstoreconnect/private_keys/AuthKey_{key_id}.p8")
    if not (key_id and issuer and os.path.exists(key_path)):
        sys.exit("ASC config missing: need ASC_KEY_ID, ASC_ISSUER_ID and a .p8 "
                 "(see module docstring)")
    return key_id, issuer, key_path


def make_token():
    key_id, issuer, key_path = _config()
    with open(key_path, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    now = int(time.time())
    header = {"alg": "ES256", "kid": key_id}  # only alg/kid; typ causes 401
    payload = {"iss": issuer, "iat": now, "exp": now + 1200,
               "aud": "appstoreconnect-v1"}
    b64 = lambda d: base64.urlsafe_b64encode(d).rstrip(b"=")
    h64 = b64(json.dumps(header, separators=(",", ":")).encode())
    p64 = b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = key.sign(h64 + b"." + p64, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig)  # JWT needs raw r||s(32B), not DER
    return (h64 + b"." + p64 + b"." +
            b64(r.to_bytes(32, "big") + s.to_bytes(32, "big"))).decode()


def request(method, path, body=None, retries=4):
    token = make_token()
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if data:
        headers["Content-Type"] = "application/json"
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
                return resp.status, (json.loads(payload) if payload else None)
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")
            if e.code in (409, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))  # transient proxy/ASC hiccups
                last = txt
                continue
            return e.code, {"error": txt[:12000]}
        except Exception as e:  # noqa: BLE001
            last = str(e)
            time.sleep(3 * (attempt + 1))
    return 0, {"error": f"unreachable after retries: {last}"}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    method, path = sys.argv[1], sys.argv[2]
    body = None
    if len(sys.argv) > 3:
        raw = sys.stdin.read() if sys.argv[3] == "-" else open(sys.argv[3]).read()
        body = json.loads(raw) if raw.strip() else None
    status, payload = request(method, path, body)
    print(json.dumps({"status": status, "body": payload}, ensure_ascii=False,
                     indent=1))
    sys.exit(0 if 200 <= status < 300 or status == 204 else 1)


if __name__ == "__main__":
    main()
