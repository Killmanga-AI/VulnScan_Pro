from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

# -----------------------------
# Database + Models imports
# -----------------------------
from app.core.database import get_db, Base, engine
from app.core.models import User, Scan
from app.services.scan_service import ScanService

# -----------------------------
# Initialize database
# -----------------------------
# Create all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# -----------------------------
# FastAPI app initialization
# -----------------------------
app = FastAPI(title="VulnScan Pro", version="1.0.0")

# -----------------------------
# Static files configuration
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory does not exist: {STATIC_DIR}")

INDEX_HTML = STATIC_DIR / "index.html"
if not INDEX_HTML.exists():
    raise RuntimeError(f"Index HTML does not exist: {INDEX_HTML}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# -----------------------------
# Request models
# -----------------------------
class ScanRequest(BaseModel):
    target_url: str

# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    return FileResponse(str(INDEX_HTML))


@app.post("/api/scans")
async def create_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """Start a vulnerability scan."""
    scan_service = ScanService(db)
    try:
        scan_id = await scan_service.start_scan(user_id=1, target_url=request.target_url)
        return {
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan started for {request.target_url}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Retrieve scan results."""
    scan_service = ScanService(db)
    results = scan_service.get_scan_results(scan_id)
    if not results:
        raise HTTPException(status_code=404, detail="Scan not found")
    return results


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "scan_credits": user.scan_credits,
        "plan_tier": user.plan_tier,
        "created_at": user.created_at
    }


@app.get("/{full_path:path}", response_class=FileResponse)
async def spa_fallback(full_path: str):
    """Fallback for single-page frontend routing."""
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404)
    return FileResponse(str(INDEX_HTML))

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)