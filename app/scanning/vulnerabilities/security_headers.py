import aiohttp
from typing import List, Dict
from datetime import datetime, timezone


async def check_insecure_headers(url: str) -> List[Dict]:
    vulnerabilities = []

    required_headers = {
        'X-Frame-Options': {
            'description': 'Prevents clickjacking attacks',
            'severity': 'MEDIUM',
            'cvss_score': 4.0
        },
        'X-Content-Type-Options': {
            'description': 'Prevents MIME type sniffing',
            'severity': 'LOW',
            'cvss_score': 2.1
        },
        'Strict-Transport-Security': {
            'description': 'Enforces HTTPS connections',
            'severity': 'HIGH',
            'cvss_score': 5.9
        },
        'Content-Security-Policy': {
            'description': 'Prevents XSS and other code injection attacks',
            'severity': 'HIGH',
            'cvss_score': 7.5
        },
        'X-XSS-Protection': {
            'description': 'Enables XSS protection in older browsers',
            'severity': 'LOW',
            'cvss_score': 2.5
        }
    }

    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                headers = response.headers

                for header, info in required_headers.items():
                    if header not in headers:
                        vulnerabilities.append({
                            'type': 'Security Header Missing',
                            'severity': info['severity'],
                            'description': f'Missing security header: {header} - {info["description"]}',
                            'location': url,
                            'cvss_score': info['cvss_score'],
                            'detected_at': datetime.now(timezone.utc).isoformat(),
                            'remediation': f'Configure {header} header in your web server settings.'
                        })
                    else:
                        # Check for weak configurations
                        header_value = headers[header].lower()

                        if header == 'X-Frame-Options' and 'deny' not in header_value and 'sameorigin' not in header_value:
                            vulnerabilities.append({
                                'type': 'Weak Security Header',
                                'severity': 'MEDIUM',
                                'description': f'Weak {header} configuration: {headers[header]}',
                                'location': url,
                                'cvss_score': 3.5,
                                'detected_at': datetime.now(timezone.utc).isoformat(),
                                'remediation': f'Set {header} to "DENY" or "SAMEORIGIN" for better protection.'
                            })

    except Exception as e:
        print(f"Security headers check failed: {e}")

    return vulnerabilities
