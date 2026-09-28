import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from ..security import hash_password, verify_password, create_jwt
from ..repositories import create_user, get_user_by_username, user_exists, list_recommendations
from ..services.auth import current_user, require_user, COOKIE_NAME
from .utils import render, login_redirect

router = APIRouter()


@router.get('/register')
def register_page(request: Request):
    if current_user(request):
        return RedirectResponse('/dashboard', status_code=303)
    return render(request, 'auth/register.html')


@router.post('/register')
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    username, email = username.strip(), email.strip().lower()
    if len(username) < 3:
        return render(request, 'auth/register.html', {'error': 'Username must be at least 3 characters.'})
    if password != confirm_password:
        return render(request, 'auth/register.html', {'error': 'Passwords do not match.'})
    if len(password) < 8:
        return render(request, 'auth/register.html', {'error': 'Password must be at least 8 characters.'})
    if user_exists(username, email):
        return render(request, 'auth/register.html', {'error': 'Username or email is already registered.'})
    user = create_user(username, email, hash_password(password))
    return login_redirect(user['id'])


@router.get('/login')
def login_page(request: Request):
    if current_user(request):
        return RedirectResponse('/dashboard', status_code=303)
    return render(request, 'auth/login.html')


@router.post('/login')
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user_by_username(username.strip())
    if not user or not verify_password(password, user['password_hash']):
        return render(request, 'auth/login.html', {'error': 'Invalid username or password.'})
    return login_redirect(user['id'])


@router.get('/logout')
def logout():
    response = RedirectResponse('/login', status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.post('/token')
async def token(request: Request):
    data = await request.json()
    user = get_user_by_username(str(data.get('username', '')).strip())
    if not user or not verify_password(str(data.get('password', '')), user['password_hash']):
        return JSONResponse({'detail': 'Invalid credentials'}, status_code=401)
    return {'access_token': create_jwt(str(user['id']), 3600), 'token_type': 'bearer'}


@router.get('/session-info')
def session_info(request: Request):
    user = current_user(request)
    return {
        'logged_in': bool(user),
        'user_id': int(user['id']) if user else None,
        'username': user['username'] if user else None,
    }


@router.get('/session-data')
def session_data(request: Request):
    user = require_user(request)
    rows = list_recommendations(user['id'], limit=5)
    return {
        'user_id': int(user['id']),
        'username': user['username'],
        'recent_recommendations': [
            {
                'id': r['id'],
                'planner_type': r['planner_type'],
                'total_budget': r['total_budget'],
                'created_at': r['created_at'],
            }
            for r in rows
        ],
    }
