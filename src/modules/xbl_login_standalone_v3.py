
# xbl_login_standalone_v3.py — Sign in to Xbox Live and save tokens
# Usage: py xbl_login_standalone_v3.py
import os, sys, asyncio, urllib.parse as up

from pythonxbox.authentication.manager import AuthenticationManager
from pythonxbox.authentication.models import OAuth2TokenResponse
from pythonxbox.common.signed_session import SignedSession

DESKTOP_REDIRECT = "https://login.live.com/oauth20_desktop.srf"

def _tokens_path() -> str:
    try:
        from platformdirs import user_data_dir
        base = user_data_dir(appname="xbox", appauthor="OpenXbox", roaming=False)
    except Exception:
        base = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "OpenXbox", "xbox")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "tokens.json")

def _client_constants():
    try:
        from pythonxbox.scripts import CLIENT_ID, CLIENT_SECRET
        return CLIENT_ID, CLIENT_SECRET
    except Exception:
        return "000000004C12AE6F", ""  # public client ID, no secret

TOKENS_FILE = _tokens_path()
CLIENT_ID, CLIENT_SECRET = _client_constants()

def _extract_code(val: str) -> str:
    s = val.strip()
    if not s:
        return ""
    if s.lower().startswith("http"):
        q = up.urlparse(s).query
        qs = up.parse_qs(q)
        return (qs.get("code") or [""])[0]
    # If they pasted a raw code with extra params like "&lc=1033", trim after first '&'
    if "&" in s and not s.lower().startswith("microsoft"):
        s = s.split("&", 1)[0]
    return s

async def amain():
    async with SignedSession() as session:
        auth = AuthenticationManager(session, CLIENT_ID, CLIENT_SECRET, DESKTOP_REDIRECT)

        # Try refresh existing tokens
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                tokens_json = f.read()
            auth.oauth = OAuth2TokenResponse.model_validate_json(tokens_json)
            try:
                await auth.refresh_tokens()
                with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                    f.write(auth.oauth.json())
                print("[OK] Already signed in. Tokens refreshed.")
                print(f"[Info] Tokens file: {TOKENS_FILE}")
                return
            except Exception:
                pass
        except FileNotFoundError:
            pass

        # Start auth
        url = auth.generate_authorization_url()
        print("=== Xbox Sign‑In ===")
        print("1) Open this URL in a browser:")
        print(url)
        print("2) Approve sign‑in; you will be redirected. If you see a code or a URL with '?code=', copy it.")
        val = input("3) Paste the code (or full URL) here, then press Enter: ").strip()
        code = _extract_code(val)
        if not code:
            print("[CANCELLED] No code detected.")
            sys.exit(1)

        try:
            tokens = await auth.request_oauth_token(code)
        except Exception as e:
            print("[ERROR] Token exchange failed.\n"
                  "Tips:\n"
                  "  • Paste a **fresh** code (codes are single‑use).\n"
                  "  • If you pasted a code with '&lc=...', only paste up to the first '&'.\n"
                  "  • Or paste the **entire** redirected URL that contains '?code=...'\n"
                  f"Detail: {e}", file=sys.stderr)
            sys.exit(1)

        auth.oauth = tokens
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            f.write(tokens.json())
        print("[OK] Signed in and tokens saved.")
        print(f"[Info] Tokens file: {TOKENS_FILE}")

def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("\n[Cancelled]")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
