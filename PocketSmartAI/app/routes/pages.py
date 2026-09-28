from fastapi import APIRouter, Request
from ..services.auth import current_user
from .utils import render, planner_page

router = APIRouter()


@router.get('/')
def home(request: Request):
    return render(request, 'home.html')


@router.get('/dashboard')
def dashboard(request: Request):
    user = current_user(request)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse('/login', status_code=303)
    return render(request, 'dashboard.html', {'user': user, 'active': 'dashboard'})


@router.get('/planner/home')
def home_planner(request: Request):
    return planner_page(request, 'planner_home.html', 'home')


@router.get('/planner/party')
def party_planner(request: Request):
    return planner_page(request, 'planner_party.html', 'party')


@router.get('/planner/jewelry')
def jewelry_planner(request: Request):
    return planner_page(request, 'planner_jewelry.html', 'jewelry')
