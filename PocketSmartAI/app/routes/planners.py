import time
from pathlib import Path
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from ..config import settings
from ..repositories import create_recommendation
from ..services.auth import current_user
from ..services.gemini import gemini_service
from ..services.recommender import home_fallback, party_fallback, jewelry_fallback
from ..models.schemas import HomePlannerInput, PartyPlannerInput
from .utils import render, safe_filename

router = APIRouter()


@router.post('/generate-home')
def generate_home(
    request: Request,
    total_budget: float = Form(...),
    lights: int = Form(0),
    ceiling_fans: int = Form(0),
    furniture: int = Form(0),
    dining_tables: int = Form(0),
    rooms: list[str] = Form([]),
    notes: str = Form(''),
):
    user = current_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    try:
        data = HomePlannerInput(
            total_budget=float(total_budget),
            lights=int(lights),
            ceiling_fans=int(ceiling_fans),
            furniture=int(furniture),
            dining_tables=int(dining_tables),
            rooms=rooms or [],
            notes=notes or '',
        ).model_dump()
    except Exception as exc:
        return render(request, 'planner_home.html', {'error': str(exc), 'user': user, 'active': 'home'})
    result = gemini_service.generate('home', data) or home_fallback(data)
    rec_id = create_recommendation(user['id'], 'Home Interior Budget', data['total_budget'], result, data)
    return render(request, 'results_home.html', {'user': user, 'active': 'home', 'result': result, 'rec_id': rec_id})


@router.post('/generate-party')
def generate_party(
    request: Request,
    total_budget: float = Form(...),
    guests: int = Form(...),
    party_type: str = Form('Birthday'),
    venue_type: str = Form('Home'),
    needs: list[str] = Form([]),
    notes: str = Form(''),
):
    user = current_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    try:
        data = PartyPlannerInput(
            total_budget=float(total_budget),
            guests=int(guests),
            party_type=party_type,
            venue_type=venue_type,
            needs=needs or [],
            notes=notes or '',
        ).model_dump()
    except Exception as exc:
        return render(request, 'planner_party.html', {'error': str(exc), 'user': user, 'active': 'party'})
    result = gemini_service.generate('party', data) or party_fallback(data)
    rec_id = create_recommendation(user['id'], 'Party Planning Budget', data['total_budget'], result, data)
    return render(request, 'results_party.html', {'user': user, 'active': 'party', 'result': result, 'rec_id': rec_id})


@router.post('/generate-jewelry')
def generate_jewelry(
    request: Request,
    total_budget: float = Form(...),
    occasion: str = Form('Birthday'),
    style_preferences: str = Form(''),
    outfit_image: UploadFile | None = File(None),
):
    user = current_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    saved = None
    if outfit_image and outfit_image.filename:
        content = outfit_image.file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            return render(request, 'planner_jewelry.html', {
                'error': f'Image must be {settings.max_upload_mb} MB or smaller.',
                'user': user,
                'active': 'jewelry',
                'max_upload_mb': settings.max_upload_mb,
            })
        if not (outfit_image.content_type or '').startswith('image/'):
            return render(request, 'planner_jewelry.html', {
                'error': 'Please upload a valid image.',
                'user': user,
                'active': 'jewelry',
                'max_upload_mb': settings.max_upload_mb,
            })
        ext = Path(safe_filename(outfit_image.filename)).suffix or '.jpg'
        saved = settings.upload_dir / f"user_{user['id']}_{time.time_ns()}{ext}"
        saved.write_bytes(content)
    data = {
        'total_budget': float(total_budget),
        'occasion': occasion,
        'style_preferences': style_preferences,
        'outfit_image': f'/uploads/{saved.name}' if saved else None,
    }
    result = gemini_service.generate('jewelry', data, image_path=str(saved) if saved else None) or jewelry_fallback(data)
    if saved:
        result['outfit_image'] = data['outfit_image']
    rec_id = create_recommendation(user['id'], 'Jewelry Budget', data['total_budget'], result, data)
    return render(request, 'results_jewelry.html', {'user': user, 'active': 'jewelry', 'result': result, 'rec_id': rec_id})
