import asyncio
import aiohttp
from datetime import datetime

from app.scanning.vulnerabilities.sql_injection import check_sql_injection
from app.scanning.vulnerabilities.xss import check_xss_vulnerabilities
from app.scanning.vulnerabilities.security_headers import check_insecure_headers


class ScanningEngine:
    def __init__(self):
        self.vulnerability_checks = [
            check_sql_injection,
            check_xss_vulnerabilities,
            check_insecure_headers
        ]

    async def scan_website(self, target_url: str):
        print(f"Scanning {target_url}...")
        vulnerabilities = []

        # Run checks concurrently
        tasks = [check(target_url) for check in self.vulnerability_checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                vulnerabilities.extend(result)

        return {
            'target_url': target_url,
            'total_vulnerabilities': len(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'risk_score' : self.calculate_risk_score(vulnerabilities),
            'scan_timestamp': datetime.now().isoformat()
        }
    def calculate_risk_score(self, vulnerabilities):
        if not vulnerabilities:
            return 0.0
        scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        total = sum(scores.get(vuln.get('severity','LOW'),1)for vuln in vulnerabilities)
        return min(total / len(vulnerabilities), 10.0)