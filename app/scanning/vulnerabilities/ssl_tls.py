import ssl
import socket
from typing import List, Dict
from datetime import datetime, timezone
from urllib.parse import urlparse


async def check_ssl_tls(url: str) -> List[Dict]:
    vulnerabilities = []

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return vulnerabilities

        # Create SSL context
        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()

                # Check certificate expiration
                if cert:
                    not_after = cert.get('notAfter')
                    if not_after:
                        from datetime import datetime
                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days

                        if days_until_expiry < 30:
                            vulnerabilities.append({
                                'type': 'SSL Certificate Expiring Soon',
                                'severity': 'MEDIUM',
                                'description': f'SSL certificate expires in {days_until_expiry} days',
                                'location': url,
                                'cvss_score': 4.0,
                                'detected_at': datetime.now(timezone.utc).isoformat(),
                                'remediation': 'Renew SSL certificate before expiration.'
                            })

                # Check cipher strength
                if cipher:
                    cipher_name = cipher[0]
                    weak_ciphers = ['RC4', 'DES', '3DES', 'NULL', 'ANON', 'EXPORT']

                    if any(weak in cipher_name for weak in weak_ciphers):
                        vulnerabilities.append({
                            'type': 'Weak SSL/TLS Cipher',
                            'severity': 'MEDIUM',
                            'description': f'Weak cipher suite detected: {cipher_name}',
                            'location': url,
                            'cvss_score': 5.0,
                            'detected_at': datetime.now(timezone.utc).isoformat(),
                            'remediation': 'Disable weak cipher suites and use modern encryption.'
                        })

    except ssl.SSLCertVerificationError:
        vulnerabilities.append({
            'type': 'Invalid SSL Certificate',
            'severity': 'HIGH',
            'description': 'SSL certificate verification failed',
            'location': url,
            'cvss_score': 7.4,
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'remediation': 'Fix SSL certificate configuration and ensure proper chain of trust.'
        })
    except Exception as e:
        print(f"SSL/TLS check failed: {e}")

    return vulnerabilities