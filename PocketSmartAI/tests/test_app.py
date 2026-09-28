import time
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db

init_db(); client=TestClient(app)


def new_user():
    username=f"qa_{time.time_ns()}"
    email=f"{username}@example.com"
    password="password123"
    return username, email, password


def test_home_health_startup_and_cors():
    assert client.get('/').status_code == 200
    assert client.get('/health').json()['status'] == 'ok'
    startup = client.get('/startup').json()
    assert startup['status'] == 'ready'
    cors = client.options('/health', headers={'Origin':'http://example.com', 'Access-Control-Request-Method':'GET'})
    assert cors.status_code == 200
    assert cors.headers.get('access-control-allow-origin') == '*'


def test_auth_and_all_planners():
    username, email, password = new_user()
    r=client.post('/register',data={'username':username,'email':email,'password':password,'confirm_password':password},follow_redirects=False)
    assert r.status_code==303
    assert client.get('/dashboard').status_code==200
    for path in ['/planner/home','/planner/party','/planner/jewelry']:
        assert client.get(path).status_code==200
    assert client.post('/generate-home',data={'total_budget':'5000','lights':'5','ceiling_fans':'4','furniture':'2','dining_tables':'1','rooms':['Living Room','Kitchen'],'notes':'warm lighting'}).status_code==200
    assert client.post('/generate-party',data={'total_budget':'5000','guests':'3','party_type':'Wedding','venue_type':'Home','needs':['catering','entertainment'],'notes':''}).status_code==200
    assert client.post('/generate-jewelry',data={'total_budget':'5000','occasion':'Birthday','style_preferences':'casual'}).status_code==200
    history = client.get('/history')
    assert history.status_code == 200
    assert 'Your Recommendation History' in history.text
    session = client.get('/session-info').json()
    assert session['logged_in'] is True
    assert session['username'] == username
    assert client.get('/session-data').json()['recent_recommendations']

    token_resp = client.post('/token', json={'username':username,'password':password})
    assert token_resp.status_code == 200
    assert token_resp.json()['token_type'] == 'bearer'
    bearer = {'Authorization': f"Bearer {token_resp.json()['access_token']}"}
    assert client.get('/session-info', headers=bearer).json()['logged_in'] is True
    assert client.get('/session-data', headers=bearer).status_code == 200

    # The latest records are user-owned and can be retrieved through the API and detail page.
    rows = client.get('/session-data').json()['recent_recommendations']
    rec_id = rows[0]['id']
    assert client.get('/recommendations-details', params={'id': rec_id}).status_code == 200
    assert client.get(f'/recommendations/{rec_id}').status_code == 200


def test_logout():
    # Register a dedicated user first so the test is independent of ordering.
    username, email, password = new_user()
    assert client.post('/register',data={'username':username,'email':email,'password':password,'confirm_password':password},follow_redirects=False).status_code == 303
    assert client.get('/logout',follow_redirects=False).status_code==303
    assert client.get('/session-info').json()['logged_in'] is False
    assert client.get('/dashboard',follow_redirects=False).status_code == 303


def test_jewelry_image_upload_and_gemini_contract(monkeypatch):
    username, email, password = new_user()
    assert client.post('/register',data={'username':username,'email':email,'password':password,'confirm_password':password},follow_redirects=False).status_code == 303
    tiny_png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\x0dIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0dIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    r = client.post('/generate-jewelry', data={'total_budget':'8000','occasion':'Wedding','style_preferences':'minimal gold'}, files={'outfit_image':('outfit.png', tiny_png, 'image/png')})
    assert r.status_code == 200
    assert '/uploads/' in r.text or 'Your Personalized Jewelry Recommendations' in r.text

    from app.services.gemini import gemini_service
    monkeypatch.setattr(gemini_service, 'enabled', True)
    monkeypatch.setattr(gemini_service, '_call', lambda prompt, image_path=None: '{"title":"AI plan","total_budget":8000,"allocated":3000,"remaining":5000,"outfit_analysis":{"colors":"blue","style":"minimal","formality":"formal"},"items":[{"name":"AI bracelet","description":"Test","price":1200,"style":"minimal","shopping_query":"AI bracelet"}],"styling_tips":["Keep it simple"]}')
    ai = gemini_service.generate('jewelry', {'total_budget':8000,'occasion':'Wedding','style_preferences':'minimal gold'})
    assert ai['ai_used'] is True
    assert ai['total_budget_display'] == '₹8,000.00'
    assert ai['items'][0]['shopping_links']

