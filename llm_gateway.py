from openai import OpenAI
import requests
import httpx
import time
import os
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# ── Credentials (loaded from .env) ────────────────────────────────────────────
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
LLM_GATEWAY_KEY = os.environ["LLM_GATEWAY_KEY"]

TENANT_ID = os.environ["TENANT_ID"]
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "https://gateway.apim.lilly.com/llm-gateway")
GATEWAY_SCOPE = os.getenv("GATEWAY_SCOPE", "api://llm-gateway.lilly.com/.default")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5.1-2025-11-13")

# ── Token cache ───────────────────────────────────────────────────────────────
_token_cache = {"token": None, "expires_at": 0}


def get_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    """Fetch an OAuth2 Bearer token from Azure AD, using cache if still valid."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": GATEWAY_SCOPE,
    }
    response = requests.post(TOKEN_URL, data=payload, verify=False)
    response.raise_for_status()
    data = response.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return _token_cache["token"]


def get_llm_client(llm_gateway_key=LLM_GATEWAY_KEY):
    """
    Authenticate and return a configured OpenAI client pointing at the
    Lilly LLM Gateway. Token is auto-refreshed when expired.

    Usage:
        from llm_gateway import get_llm_client, DEFAULT_MODEL

        client = get_llm_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    access_token = get_access_token()
    client = OpenAI(
        api_key=llm_gateway_key,
        base_url=GATEWAY_BASE_URL,
        http_client=httpx.Client(verify=False),
        default_headers={
            "Authorization": f"Bearer {access_token}",
            "X-LLM-Gateway-Key": llm_gateway_key,
        },
    )
    return client


# ── Connection test (runs only when executed directly) ────────────────────────
if __name__ == "__main__":
    try:
        client = get_llm_client()
        # Minimal ping to verify the connection end-to-end
        client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=500,
        )
        print("Successful connection")
    except Exception as e:
        print(f"Connection failed: {e}")
