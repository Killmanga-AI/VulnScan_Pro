from sqlalchemy.orm import Session
import asyncio

from app.core.database import User, Scan, Vulnerability, SessionLocal
from app.scanning.engine import ScanningEngine

class ScanService:
    def __init__(self, db: Session):
        self.db = db
        self.scanner = ScanningEngine()

    async def start_scan(self, user_id: int, target_url: str):
        # Check user credits (using my integrated Scan model)
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.scan_credits <= 0:
            raise ValueError("No scan credits for this user")


        #Create scan record (using your integrated Scan model)
        scan = Scan(
            target_url=target_url,
            user_id=user.id,
            status="running",
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)


        try:
            #Use your scanner(this stays the same)
            results = await self.scanner.scan_website(target_url)

            #Save vulnerabilities(using my integrated Vulnerability model)
            for vuln in results['vulnerabilities']:
                db_vuln = Vulnerability(
                    scan_id=scan.id,
                    vulnerabilitiy_type=vuln['type'],
                    severity=vuln['severity'],
                    description=vuln['description'],
                    location=vuln['location'],
                    cvss_score = vuln.get('cvss_score',0.0),
                )
                self.db.add(db_vuln)

                #Deduct scan with results
                scan.status = "completed"
                scan.vulnerabilities_found = results['total_vulnerabilities']
                scan.risk_score = results['risk_score']

                #Dedyct credit
                user.scan_credits -= 1

                self.db.commit()

        except Exception as e:
            scan.status = "failed"
            self.db.commit()
            raise e
        return  scan.id

    def get_scan_results(self, scan_id: int):
        #Get scan with vulnerabilities(using my integrated models)
        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return None

        vulnerabilities = self.db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()

        return {
            'scan_id': scan.id,
            'target_url': scan.target_url,
            'status': scan.status,
            'vulnerabilities_found': scan.vulnerabilities_found,
            'risk_score': scan.risk_score,
            'created_at': scan.created_at,
            'vulnerabilities':[
                {

                    'type': vuln.vulnerability_type,
                    'description': vuln.description,
                    'location': vuln.location,
                    'cvss_scored': vuln.cvss_score,
                }
                for vuln in vulnerabilities
            ]
        }

