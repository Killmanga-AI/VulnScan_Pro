import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.scanning.vulnerabilities.sql_injection import check_sql_injection
from app.scanning.vulnerabilities.xss import check_xss_vulnerabilities
from app.scanning.vulnerabilities.security_headers import check_insecure_headers

# Import models from models.py
from app.core.models import User, Scan, Vulnerability


class ScanService:
    def __init__(self, db: Session):
        self.db = db
        # List of all vulnerability check functions
        self.vulnerability_checks = [
            check_sql_injection,
            check_xss_vulnerabilities,
            check_insecure_headers
        ]

    async def start_scan(self, user_id: int, target_url: str) -> int:
        """Create a new scan and run vulnerability checks asynchronously."""
        # Fetch user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        # Create Scan record
        scan = Scan(
            target_url=target_url,
            user_id=user.id,
            status="running",
            vulnerabilities_found=0,
            risk_score=0.0,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)  # Refresh to get scan.id

        # Run async vulnerability checks
        scan_result = await self._run_checks(scan)

        return scan.id

    async def _run_checks(self, scan: Scan) -> dict:
        """Run all vulnerability checks concurrently and save results."""
        tasks = [check(scan.target_url) for check in self.vulnerability_checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        vulnerabilities_count = 0
        risk_score_total = 0

        for result in results:
            if isinstance(result, list):
                for vuln_data in result:
                    vuln = Vulnerability(
                        scan_id=scan.id,
                        vulnerability_type=vuln_data.get("type"),
                        severity=vuln_data.get("severity"),
                        description=vuln_data.get("description"),
                        location=vuln_data.get("location"),
                        cvss_score=vuln_data.get("cvss_score"),
                        created_at=datetime.now(timezone.utc)
                    )
                    self.db.add(vuln)
                    vulnerabilities_count += 1
                    # Simple scoring: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4
                    severity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
                    risk_score_total += severity_map.get(vuln.severity, 1)

        # Update Scan record
        scan.vulnerabilities_found = vulnerabilities_count
        scan.risk_score = min(risk_score_total / max(vulnerabilities_count, 1), 10.0)
        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(scan)

        return {
            "scan_id": scan.id,
            "target_url": scan.target_url,
            "total_vulnerabilities": vulnerabilities_count,
            "risk_score": scan.risk_score
        }

    def get_scan_results(self, scan_id: int) -> dict | None:
        """Retrieve scan results by scan ID."""
        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return None

        vulnerabilities = (
            self.db.query(Vulnerability)
            .filter(Vulnerability.scan_id == scan.id)
            .all()
        )

        return {
            "scan_id": scan.id,
            "target_url": scan.target_url,
            "status": scan.status,
            "risk_score": scan.risk_score,
            "vulnerabilities_found": scan.vulnerabilities_found,
            "vulnerabilities": [
                {
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "description": v.description,
                    "location": v.location,
                    "cvss_score": v.cvss_score
                }
                for v in vulnerabilities
            ],
            "created_at": scan.created_at,
            "completed_at": scan.completed_at
        }