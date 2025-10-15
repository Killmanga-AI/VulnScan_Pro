import aiohttp

async def check_sql_injection(url: str):
    vulnerabilities = []
    test_payloads = ["' OR '1'='1:", "' UNION SELECT 1,2,3--"]

    try:
        async with aiohttp.ClientSession() as session:
            for payload in test_payloads:
                test_url = f"{url}?id={payload}"
                async with session.get(test_url) as response:
                    text_url = await response.text()
                    if any(error in text.lower() for error in ["sql syntax","mysql_fetch", "ora-"]):
                        vulnerabilities.append({
                            'type': 'SQL Injection',
                            'severity': 'HIGH',
                            'description': f'Potential SQL Injection with payload: {payload}',
                            'location': test_url,
                            'cvss_score': 8.2
                        })
    except Exception as e:
        print(f"SQL injection check failed: {e}")

    return vulnerabilities