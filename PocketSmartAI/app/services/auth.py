from fastapi import HTTPException, Request
from ..repositories import get_user_by_id
from ..security import verify_jwt

COOKIE_NAME = "pocketsmart_session"

def _token_from_request(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None

def current_user(request: Request):
    token = _token_from_request(request)
    if not token:
        return None
    payload = verify_jwt(token)
    if not payload:
        return None
    try:
        return get_user_by_id(int(payload["sub"]))
    except (KeyError, TypeError, ValueError):
        return None

def require_user(request: Request):
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
