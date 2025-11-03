from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.database import Base, engine
from app.routes import auth_routes, scan_routes
import pathlib

# Initialize DB
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="VulnScan Pro", version="1.0")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Static Files Configuration
# ------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve Frontend (index.html)
@app.get("/", include_in_schema=False)
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail=f"index.html not found at {index_path}")

# ------------------------------
# Routers
# ------------------------------
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(scan_routes.router, prefix="/api/scan", tags=["Scanner"])

# ------------------------------
# Debug on startup
# ------------------------------
@app.on_event("startup")
def log_static_path():
    print(f" Static files being served from: {STATIC_DIR}")
    print(f" Index file expected at: {STATIC_DIR / 'index.html'}")
