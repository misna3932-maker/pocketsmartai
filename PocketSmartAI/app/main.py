from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import init_db
from .routes import auth, history, pages, planners
from .services.gemini import gemini_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version='1.0.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['*'],
)

BASE = Path(__file__).resolve().parent
app.mount('/static', StaticFiles(directory=str(BASE / 'static')), name='static')
app.mount('/uploads', StaticFiles(directory=str(settings.upload_dir)), name='uploads')

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)


@app.get('/health')
def health():
    return {'status': 'ok', 'app': settings.app_name, 'gemini_enabled': gemini_service.enabled}


@app.get('/startup')
def startup_status():
    """Expose the source plan's startup/service-readiness concept for health checks."""
    return {
        'status': 'ready',
        'database': str(settings.database_path),
        'upload_directory': str(settings.upload_dir),
        'gemini_enabled': gemini_service.enabled,
    }
