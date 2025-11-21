
import json, requests, pathlib, os

XBL_USER_AUTH = "https://user.auth.xboxlive.com/user/authenticate"
XBL_XSTS_AUTH = "https://xsts.auth.xboxlive.com/xsts/authorize"

# Explicit HTTP timeout (seconds) for Xbox Live auth calls
_HTTP_TIMEOUT = 10

def get_xsts_from_tokens(tokens_path):
    tokens_path = pathlib.Path(tokens_path)
    data = json.loads(tokens_path.read_text())
    access = data["access_token"]
    # user token
    payload_user = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={access}"
        }
    }
    r = requests.post(XBL_USER_AUTH, json=payload_user, headers={"Content-Type":"application/json"}, timeout=_HTTP_TIMEOUT)
    r.raise_for_status()
    j = r.json()
    user_token = j["Token"]
    uhs = j["DisplayClaims"]["xui"][0]["uhs"]

    # xsts
    payload_xsts = {
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL"
        }
    }
    r2 = requests.post(XBL_XSTS_AUTH, json=payload_xsts, headers={"Content-Type":"application/json"}, timeout=_HTTP_TIMEOUT)
    r2.raise_for_status()
    j2 = r2.json()
    xsts = j2["Token"]
    uhs2 = j2["DisplayClaims"]["xui"][0]["uhs"]
    return {"Authorization": f"XBL3.0 x={uhs2};{xsts}"}
