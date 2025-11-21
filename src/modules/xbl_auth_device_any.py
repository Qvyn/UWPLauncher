
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
        # Surface MSAL error details so it isn't a silent failure.
        print("Device flow failed to start for client_id", client_id, file=sys.stderr)
        print("Raw response:", flow, file=sys.stderr)
        return False
    print("\n=== Microsoft Sign-in ===")
    print("Go to:", flow["verification_uri"])
    print("Enter code:", flow["user_code"])
    print("Then return here; this window will finish automatically.\n")
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        print("Sign-in failed for client_id", client_id, file=sys.stderr)
        print("Raw response:", result, file=sys.stderr)
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
    ap.add_argument("--client-id", help="Override the default Xbox client id (advanced users with their own Azure app)")
    args = ap.parse_args()

    # If the user provides a custom client id, try only that one.
    if args.client_id:
        ok = run_device_flow(args.client_id, args.out)
        if ok:
            return
        print("Device flow failed for the provided client id. See error details above.", file=sys.stderr)
        sys.exit(2)

    # Otherwise, fall back to the built-in public Xbox client ids.
    for cid in CANDIDATE_CLIENT_IDS:
        ok = run_device_flow(cid, args.out)
        if ok:
            return
        else:
            print(f"Client {cid} failed, trying next…")
    print(
        "All built-in Xbox client IDs failed. Microsoft currently returns 'unauthorized_client' for these public ids. "
        "Use an existing tokens.json (for example from OpenXbox tooling) or provide your own Azure app client id "
        "via --client-id.",
        file=sys.stderr,
    )
    sys.exit(2)

if __name__ == "__main__":
    main()
