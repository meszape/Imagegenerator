from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import routes_health, routes_sessions, routes_images
from app.config import get_settings
from app.core.exceptions import AppError
from app.logging import configure_logging
from app.storage.db import init_db
configure_logging(get_settings().log_level)
app=FastAPI(title='Multi-provider Image Orchestrator', version='0.1.0')
@app.on_event('startup')
def startup(): init_db()
@app.exception_handler(AppError)
def app_error(_:Request, exc:AppError): return JSONResponse(status_code=exc.status_code, content={'code':exc.code,'message':exc.message,'provider':exc.provider,'details':exc.details})
app.include_router(routes_health.router); app.include_router(routes_sessions.router); app.include_router(routes_images.router)
