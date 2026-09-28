import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from ..repositories import get_recommendation, list_recommendations
from ..services.auth import current_user, require_user
from .utils import render

router = APIRouter()


@router.get('/recommendations-details')
def recommendations_details_api(request: Request, id: int):
    user = require_user(request)
    row = get_recommendation(id, user['id'])
    if not row:
        return JSONResponse({'detail': 'Recommendation not found'}, status_code=404)
    return json.loads(row['payload_json'])


@router.get('/recommendations/{rec_id}')
def recommendation_detail(request: Request, rec_id: int):
    user = current_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    row = get_recommendation(rec_id, user['id'])
    if not row:
        return RedirectResponse('/history', status_code=303)
    result = json.loads(row['payload_json'])
    planner = row['planner_type'].lower()
    if 'home' in planner:
        template, active = 'results_home.html', 'home'
    elif 'party' in planner:
        template, active = 'results_party.html', 'party'
    else:
        template, active = 'results_jewelry.html', 'jewelry'
    return render(request, template, {'user': user, 'active': active, 'result': result, 'rec_id': rec_id})


@router.get('/history')
def history(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse('/login', status_code=303)
    rows = []
    for r in list_recommendations(user['id']):
        payload, req = json.loads(r['payload_json']), json.loads(r['request_json'])
        planner = r['planner_type'].lower()
        if 'home' in planner:
            summary = f"Rooms: {', '.join(req.get('rooms', [])) or 'Not specified'}"
            tags = [x['category'].lower().replace(' ', '_') for x in payload.get('budget_breakdown', [])[:3]]
        elif 'party' in planner:
            summary = f"Party Type: {req.get('party_type')} • Guests: {req.get('guests')}"
            tags = req.get('needs', []) or ['venue']
        else:
            summary = f"Occasion: {req.get('occasion')} • With outfit image: {'Yes' if req.get('outfit_image') else 'No'}"
            tags = ['jewelry']
        rows.append({
            'id': r['id'],
            'planner_type': r['planner_type'],
            'created_at': r['created_at'],
            'total_budget': r['total_budget'],
            'remaining': payload.get('remaining', 0),
            'summary': summary,
            'tags': tags,
        })
    return render(request, 'history.html', {'user': user, 'active': 'history', 'rows': rows})
