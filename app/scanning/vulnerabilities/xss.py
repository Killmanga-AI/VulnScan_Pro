import aiohttp
import asyncio
from urllib.parse import urlparse, quote_plus
from typing import List, Dict
from datetime import datetime, timezone


def normalize_url(raw_url: str) -> str:
    """Ensure URL has scheme and no trailing slash."""
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Empty URL")
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        raw_url = "https://" + raw_url
    return raw_url.rstrip("/")


async def check_xss_vulnerabilities(url: str) -> List[Dict]:
    vulnerabilities = []

    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>"
    ]

    timeout = aiohttp.ClientTimeout(total=10)

    try:
        base = normalize_url(url)
    except Exception as e:
        print(f"XSS check: invalid url '{url}': {e}")
        return vulnerabilities

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for payload in xss_payloads:
                # Test in query parameter
                encoded = quote_plus(payload)
                test_url = f"{base}?q={encoded}"

                try:
                    async with session.get(test_url, allow_redirects=True) as resp:
                        body = await resp.text(errors="ignore")

                        # Check if payload is reflected without sanitization
                        if payload in body:
                            # Additional check: look for common sanitization attempts
                            sanitized_indicators = ['<', '>', '&', '&#x']
                            is_sanitized = any(indicator in body for indicator in sanitized_indicators)

                            if not is_sanitized:
                                vulnerabilities.append({
                                    "type": "Cross-Site Scripting (XSS)",
                                    "severity": "HIGH",
                                    "description": f"Reflected XSS vulnerability detected with payload: {payload}",
                                    "location": test_url,
                                    "cvss_score": 7.5,
                                    "detected_at": datetime.now(timezone.utc).isoformat(),
                                    "remediation": "Implement proper input sanitization and output encoding. Use Content Security Policy (CSP) headers."
                                })

                except asyncio.TimeoutError:
                    print(f"XSS check: timeout for {test_url}")
                except Exception as e:
                    print(f"XSS check: error testing {test_url}: {e}")

    except Exception as e:
        print(f"XSS check failed (session): {e}")

    return vulnerabilities