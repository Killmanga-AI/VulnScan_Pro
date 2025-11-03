# app/routes/scan_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.models import User, Scan, Vulnerability
from app.core.auth import decode_access_token
from app.services.scan_service import ScanService

router = APIRouter(prefix="/api", tags=["scans"])

# Dependency: read token from Authorization header manually (expects "Bearer <token>")
from fastapi import Header

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """
    Decode Authorization header (Bearer token) and return User instance.
    Raises 401 if token is invalid or user not found.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = parts[1]
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


class ScanRequestIn(BaseModel):
    target_url: str


# Create a scan (protected)
@router.post("/scans")
async def create_scan(request: Dict[str, Any], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Start a scan for the authenticated user.
    Expects JSON: { "target_url": "https://example.com" }
    Deducts a scan credit and starts the scan (async).
    """
    # minimal validation
    target_url = request.get("target_url") if isinstance(request, dict) else None
    if not target_url:
        raise HTTPException(status_code=400, detail="Missing target_url")

    # check scan credits
    if current_user.scan_credits <= 0:
        raise HTTPException(status_code=403, detail="No scan credits remaining")

    # Deduct one credit and commit
    current_user.scan_credits = current_user.scan_credits - 1
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # Create service and start scan
    scan_service = ScanService(db)
    # start_scan returns scan id (async)
    try:
        scan_id = await scan_service.start_scan(user_id=current_user.id, target_url=target_url)
    except ValueError as e:
        # refund credit on failure
        current_user.scan_credits = current_user.scan_credits + 1
        db.add(current_user)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # refund and raise
        current_user.scan_credits = current_user.scan_credits + 1
        db.add(current_user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to start scan")

    return {"scan_id": scan_id, "status": "started", "message": f"Scan started for {target_url}"}


# Get scan results (protected)
@router.get("/scans/{scan_id}")
def get_scan(scan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # ensure scan belongs to user (or is public depending on your policy)
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan")

    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()
    vulns_serialized = []
    for v in vulnerabilities:
        vulns_serialized.append({
            "vulnerability_type": v.vulnerability_type,
            "severity": v.severity,
            "description": v.description,
            "location": v.location,
            "cvss_score": v.cvss_score,
            "created_at": v.created_at.isoformat() if v.created_at else None
        })

    return {
        "scan_id": scan.id,
        "target_url": scan.target_url,
        "status": scan.status,
        "risk_score": scan.risk_score,
        "vulnerabilities_found": scan.vulnerabilities_found,
        "vulnerabilities": vulns_serialized,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None
    }

