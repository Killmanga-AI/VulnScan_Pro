# app/routes/__init__.py
from .auth_routes import router as auth_router
from .scan_routes import router as scan_router

__all__ = ["auth_router","scan_router"]