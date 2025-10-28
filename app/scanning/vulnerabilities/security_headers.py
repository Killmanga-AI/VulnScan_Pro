import aiohttp

async def check_insecure_headers(url: str):
    """Check for security headers misconfigurations"""
    vulnerabilities = []
    required_headers = {
        'X-Frame-Options': 'Prevents clickjacking',
        'X-Content-Type-Options': 'Prevents MIME sniffing',
        'Strict-Transport-Security': 'Enforces HTTPS',
        'Content-Security-Policy': 'Prevents XSS and other attacks',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                headers = response.headers

                for header, purpose in required_headers.items():
                    if header in headers:
                        vulnerabilities.append({
                            'type': 'Security Header Missing',
                            'severity': 'LOW',
                            'description': f'Missing header: {header} - {purpose}',
                            'location': url,
                            'cvss_score' : 2.5
                        })

    except Exception as e:
        print(f"Header check failed: {e}")

    return vulnerabilities
