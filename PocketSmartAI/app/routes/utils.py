import re
from pathlib import Path
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..config import settings
from ..security import create_jwt
from ..services.auth import current_user, COOKIE_NAME

BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / 'templates'))


def render(request: Request, template: str, context: dict | None = None):
    ctx = dict(context or {})
    ctx['request'] = request
    return templates.TemplateResponse(request=request, name=template, context=ctx)


def login_redirect(user_id: int, path: str = '/dashboard'):
    response = RedirectResponse(path, status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        create_jwt(str(user_id), 60 * 60 * 24 * 7),
        httponly=True,
        samesite='lax',
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )
    return response


def safe_filename(name: str):
    return re.sub(r'[^a-zA-Z0-9._-]', '_', name or 'upload.jpg')


def require_planner_user(request: Request):
    user = current_user(request)
    if not user:
        return None
    return user


def planner_page(request: Request, template: str, active: str):
    user = require_planner_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    ctx = {'user': user, 'active': active}
    if active == 'jewelry':
        ctx['max_upload_mb'] = settings.max_upload_mb
    return render(request, template, ctx)
