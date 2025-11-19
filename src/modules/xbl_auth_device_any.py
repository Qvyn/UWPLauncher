
import argparse, json, sys, time

CANDIDATE_CLIENT_IDS = [
    "00000000402B5328",  # Xbox app (commonly used for MSA device flow)
    "000000004C12AE6F",  # Alternate public Xbox client id
]

def run_device_flow(client_id: str, out_path: str) -> bool:
    try:
        import msal
    except ImportError:
        print("This script requires 'msal'. Install with:  py -m pip install msal", flush=True)
        return False
    app = msal.PublicClientApplication(client_id, authority="https://login.microsoftonline.com/consumers")
    # IMPORTANT: Do NOT include reserved scopes (openid, profile, offline_access)
    scopes = ["XboxLive.signin"]
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        return False
    print("\n=== Microsoft Sign-in ===")
    print("Go to:", flow["verification_uri"])
    print("Enter code:", flow["user_code"])
    print("Then return here; this window will finish automatically.\n")
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        print("Sign-in failed:", result, file=sys.stderr)
        return False
    data = {
        "access_token": result["access_token"],
        "refresh_token": result.get("refresh_token",""),
        "expires_at": int(time.time()) + int(result.get("expires_in", 28800)),
        "obtained_at": int(time.time()),
        "token_type": result.get("token_type","Bearer"),
        "scope": result.get("scope","XboxLive.signin"),
        "client_id": client_id,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote fresh tokens to: {out_path} (client_id={client_id})")
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tokens.json", help="Where to write tokens.json")
    args = ap.parse_args()
    for cid in CANDIDATE_CLIENT_IDS:
        ok = run_device_flow(cid, args.out)
        if ok:
            return
        else:
            print(f"Client {cid} failed, trying next…")
    print("All client IDs failed. Ensure you are on a Microsoft Account (MSA) and try again.", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    main()
