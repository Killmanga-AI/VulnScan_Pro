# app/scanning/vulnerabilities/sql_injection.py
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
        # default to https for safety — change if you need http
        raw_url = "https://" + raw_url
    return raw_url.rstrip("/")

async def check_sql_injection(url: str) -> List[Dict]:
    vulnerabilities = []

    test_payloads = [
        "' OR '1'='1",
        "' UNION SELECT NULL--",
        '" OR "1"="1',
        "' OR 1=1 --",
        "'; DROP TABLE users; --"  # don't actually run DB commands; this is only appended to URL
    ]

    sql_errors = [
        "sql syntax", "mysql_fetch", "ora-", "microsoft odbc", "postgresql error",
        "warning: mysql", "you have an error in your sql syntax",
        "unclosed quotation mark after the character string",
        "syntax error at or near"
    ]

    timeout = aiohttp.ClientTimeout(total=12)

    try:
        base = normalize_url(url)
    except Exception as e:
        print(f"SQL injection check: invalid url '{url}': {e}")
        return vulnerabilities

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for payload in test_payloads:
                # Properly encode payload into query parameter
                encoded = quote_plus(payload)
                test_url = f"{base}?id={encoded}"
                try:
                    async with session.get(test_url, allow_redirects=True) as resp:
                        status = resp.status
                        body = await resp.text(errors="ignore")
                        body_lower = body.lower()

                        # If server returned obvious SQL error strings
                        if any(err in body_lower for err in sql_errors):
                            vulnerabilities.append({
                                "type": "SQL Injection",
                                "severity": "HIGH",
                                "description": f"Potential SQL Injection with payload: {payload}",
                                "location": test_url,
                                "cvss_score": 8.2,
                                "detected_at": datetime.now(timezone.utc).isoformat()
                            })
                            # skip to next payload after detection
                            continue

                        # Reflection check — payload shows up in response
                        if payload.lower() in body_lower:
                            vulnerabilities.append({
                                "type": "SQL Injection (reflection)",
                                "severity": "MEDIUM",
                                "description": f"Payload reflected in response (possible injection point): {payload}",
                                "location": test_url,
                                "cvss_score": 5.0,
                                "detected_at": datetime.now(timezone.utc).isoformat()
                            })

                        # Optionally, you can store status codes for debugging
                        if status >= 400:
                            # server returned an error code, log for debugging but don't necessarily treat it as vuln
                            print(f"SQL injection check: got status {status} for {test_url}")

                except asyncio.TimeoutError:
                    print(f"SQL injection check: timeout for {test_url}")
                except aiohttp.ClientConnectorError as e:
                    print(f"SQL injection check: connection error for {test_url}: {e}")
                except aiohttp.ClientResponseError as e:
                    print(f"SQL injection check: response error for {test_url}: {e}")
                except Exception as e:
                    # Print some snippet of response or the exception for debugging
                    print(f"SQL injection check: error testing {test_url}: {e}")

    except Exception as e:
        print(f"SQL injection check failed (session): {e}")

    return vulnerabilities