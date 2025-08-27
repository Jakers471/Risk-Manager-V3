import json, os, requests, time
AUTH_FILE = os.path.join("runtime","auth.json")
BASE = os.getenv("PROJECTX_BASE_URL", "https://api.topstepx.com")
CONNECT_TIMEOUT = float(os.getenv("PX_CONNECT_TIMEOUT","2"))
READ_TIMEOUT    = float(os.getenv("PX_READ_TIMEOUT","5"))
_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

def _load_cache():
    try:
        with open(AUTH_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(data):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    with open(AUTH_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f)

def _is_jwt(tok:str) -> bool:
    return isinstance(tok,str) and tok.count(".")==2

def get_bearer() -> str:
    """
    Source of truth for the bearer token:
    1) runtime/auth.json: {"token":"..."}
    2) env PROJECTX_API_KEY (if it *is* a JWT)
    """
    c = _load_cache()
    tok = c.get("token") or os.getenv("PROJECTX_API_KEY","")
    return tok

def set_bearer(tok: str):
    c = _load_cache(); c["token"] = tok; _save_cache(c)

def validate_and_refresh(tok: str) -> str:
    """
    POST /api/Auth/validate
    Returns 200 and often a new token in body; if not, keep the same.
    """
    if not _is_jwt(tok):
        # Not a JWT: cannot validate; caller must supply a real JWT first.
        return tok
    url = f"{BASE}/api/Auth/validate"
    r = requests.post(url, headers={
        "accept":"text/plain",
        "Content-Type":"application/json",
        "Authorization": f"Bearer {tok}"
    }, json={}, timeout=_TIMEOUT)
    if r.status_code == 200 and r.text.strip():
        return r.text.strip()
    r.raise_for_status()
    return tok

def auth_headers() -> dict:
    tok = get_bearer()
    # one opportunistic refresh on each process start / call site
    try:
        new_tok = validate_and_refresh(tok)
        if new_tok and new_tok != tok:
            set_bearer(new_tok)
            tok = new_tok
    except Exception:
        # if validate fails (expired/401) we keep the old token;
        # caller will still get 401 and can prompt the user.
        pass
    return {"accept":"text/plain","Content-Type":"application/json",
            **({"Authorization":f"Bearer {tok}"} if tok else {})}

class AuthManager:
    """Authentication manager for CLI compatibility."""
    
    def __init__(self, config):
        """Initialize auth manager with config."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token = get_bearer()
        return bool(token and _is_jwt(token))
    
    def authenticate(self, username: str, api_key: str) -> bool:
        """Authenticate with username and API key."""
        try:
            url = f"{BASE}/api/Auth/loginKey"
            data = {
                "userName": username,
                "apiKey": api_key
            }
            
            response = requests.post(url, json=data, timeout=_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success") and result.get("token"):
                set_bearer(result["token"])
                return True
            return False
        except Exception:
            return False
    
    def get_session(self):
        """Get authenticated session."""
        token = get_bearer()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        return self.session
    
    def validate_token(self) -> bool:
        """Validate current token."""
        try:
            token = get_bearer()
            if not token or not _is_jwt(token):
                return False
            
            new_token = validate_and_refresh(token)
            if new_token != token:
                set_bearer(new_token)
            return True
        except Exception:
            return False
    
    def refresh_token(self) -> bool:
        """Refresh authentication token."""
        try:
            # Try to authenticate using config credentials
            username = self.config.get("auth.userName", "")
            api_key = self.config.get("auth.api_key", "")
            
            if username and api_key:
                return self.authenticate(username, api_key)
            return False
        except Exception:
            return False
