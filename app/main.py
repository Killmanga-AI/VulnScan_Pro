from pathlib import Path
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

# Database imports
from app.core.database import get_db, User, Scan
from app.services.scan_service import ScanService

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="VulnScan Pro", version="1.0.0")

# Verify static folder
if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory does not exist: {STATIC_DIR}")

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


INDEX_HTML = STATIC_DIR / "index.html"
if not INDEX_HTML.exists():
    raise RuntimeError(f"Index HTML does not exist: {INDEX_HTML}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(str(INDEX_HTML))

# Fixed fallback route
@app.get("/{full_path:path}", response_class=FileResponse)
async def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404)
    return FileResponse(str(INDEX_HTML))

# -------------------------------
# API Endpoints
# -------------------------------

@app.post("/api/scans")
async def create_scan(target_url: str, db: Session = Depends(get_db)):
    scan_service = ScanService(db)
    try:
        scan_id = await scan_service.start_scan(user_id=1, target_url=target_url)
        return {"scan_id": scan_id, "status": "started", "message": f"Scan started for {target_url}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "VulnScan Pro"}


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan_service = ScanService(db)
    results = scan_service.get_scan_results(scan_id)
    if not results:
        raise HTTPException(status_code=404, detail="Scan not found")
    return results

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "scan_credits": user.scan_credits,
        "plan_tier": user.plan_tier
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)