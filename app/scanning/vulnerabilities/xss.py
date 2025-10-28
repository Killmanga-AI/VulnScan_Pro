import aiohttp

async def check_xss_vulnerabilities(url: str):
    """Check for Cross-site Scripting vulnerabilities"""
    vulnerabilities = []
    xss_payloads = [
        "<script>alert('XSS');</script>",
        "img src=x one error=alert('XSS')>",
        "svg onload=alert('XSS')>",
    ]

    try:
        async with aiohttp.ClientSession() as session:
            for payload in xss_payloads:
                test_url = f"{url}?search={payload}"
                async with session.get(test_url) as response:
                    text = await response.text()

                    if payload in text and 'sanitize' not in text.lower():
                        vulnerabilities.append({
                            'type': 'Cross-site Scripting vulnerability(XSS)',
                            'severity': 'MEDIUM',
                            'description': f'Reflected XSS vulnerability in detected with payload: {payload}',
                            'location': test_url,
                            'cvss_score': 6.1
                        })

    except Exception as e:
        print(f"XSS check failed: {e}")

    return vulnerabilities