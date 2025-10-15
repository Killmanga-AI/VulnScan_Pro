from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# All imports from my integrated database
from app.core.database import get_db, User, Scan
from app.services.scan_services import ScanService

app = FastAPI(title="VulnScan Pro", version="1.0.0")

@app.post("/api/scans")
async def create_scan(target_url: str, db: Session = Depends(get_db)):
    scan_service = ScanService(db)
    try:
        scan_id = await scan_service.start_scan(user_id=1, target_url=target_url)
        return {"scan_id": scan_id, "status": "started", "message": f"Scan started for {target_url}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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