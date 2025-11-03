async function startScan() {
    const targetUrl = document.getElementById('targetUrl').value;
    const button = document.querySelector('button');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    if (!targetUrl) {
        alert('Please enter a website URL');
        return;
    }

    // Show loading, disable button
    button.disabled = true;
    button.textContent = 'Scanning...';
    loading.style.display = 'block';
    results.style.display = 'none';

    try {
        // Call your backend API
        const response = await fetch(`/api/scans`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target_url: targetUrl })
        });

        if (!response.ok) {
            throw new Error('Scan failed: ' + response.statusText);
        }

        const data = await response.json();

        // Wait a moment then get results
        setTimeout(() => {
            getScanResults(data.scan_id);
        }, 2000);

    } catch (error) {
        console.error('Scan error:', error);
        alert('Scan failed: ' + error.message);
        resetUI();
    }
}

async function getScanResults(scanId) {
    try {
        const response = await fetch(`/api/scans/${scanId}`);

        if (!response.ok) {
            throw new Error('Failed to get results');
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Results error:', error);
        alert('Failed to get scan results');
    } finally {
        resetUI();
    }
}

function displayResults(data) {
    const results = document.getElementById('results');
    const content = document.getElementById('resultsContent');

    // Calculate risk level
    const riskScore = data.risk_score || 0;
    let riskLevel = 'low';
    if (riskScore >= 7.5) riskLevel = 'critical';
    else if (riskScore >= 5) riskLevel = 'high';
    else if (riskScore >= 2.5) riskLevel = 'medium';

    let html = `
        <div class="scan-header">
            <h2>🔍 Security Scan Report</h2>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p><strong>Target:</strong> ${data.target_url || 'Unknown'}</p>
                    <p><strong>Scan Date:</strong> ${new Date().toLocaleDateString()}</p>
                </div>
                <div style="text-align: right;">
                    <div class="severity-badge badge-${riskLevel}">
                        ${riskLevel.toUpperCase()} RISK
                    </div>
                    <h3 style="margin: 5px 0;">${riskScore}/10</h3>
                </div>
            </div>
        </div>

        <div class="risk-meter">
            <div class="risk-fill" style="width: ${riskScore * 10}%"></div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #6c757d;">Vulnerabilities</h4>
                <div style="font-size: 24px; font-weight: bold; color: #dc3545;">${data.vulnerabilities_found || 0}</div>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #6c757d;">Risk Score</h4>
                <div style="font-size: 24px; font-weight: bold; color: #fd7e14;">${riskScore}/10</div>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #6c757d;">Status</h4>
                <div style="font-size: 24px; font-weight: bold; color: #28a745;">Completed</div>
            </div>
        </div>
    `;

    if (data.vulnerabilities && data.vulnerabilities.length > 0) {
        html += `<h3>📋 Detected Vulnerabilities</h3>`;

        data.vulnerabilities.forEach((vuln, index) => {
            html += `
                <div class="vulnerability ${vuln.severity.toLowerCase()}">
                    <div style="display: flex; justify-content: between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 10px 0;">
                                <span class="severity-badge badge-${vuln.severity.toLowerCase()}">
                                    ${vuln.severity}
                                </span>
                                ${vuln.type}
                            </h4>
                            <p style="margin: 5px 0; color: #666;"><strong>Location:</strong> ${vuln.location}</p>
                            <p style="margin: 10px 0;">${vuln.description}</p>

                            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                <strong>🛡️ Recommendation:</strong><br>
                                ${getRemediationAdvice(vuln.type)}
                            </div>

                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <small><strong>CVSS Score:</strong> ${vuln.cvss_score || 'N/A'}</small>
                                <small><strong>Vulnerability ID:</strong> VULN-${(index + 1).toString().padStart(3, '0')}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
            <div style="margin-top: 20px; text-align: center;">
                <button class="btn btn-primary" onclick="exportReport()">📄 Export PDF Report</button>
                <button class="btn btn-success" onclick="scanAgain()">🔍 Scan Another Website</button>
            </div>
        `;
    } else {
        html += `
            <div class="vulnerability low" style="text-align: center; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 20px;">✅</div>
                <h3 style="color: #28a745;">No Security Vulnerabilities Detected</h3>
                <p>Your website passed all security checks. Good job maintaining security best practices!</p>
                <button class="btn btn-success" onclick="scanAgain()">🔍 Scan Another Website</button>
            </div>
        `;
    }

    content.innerHTML = html;
    results.style.display = 'block';
}

// Added remediation advice function
function getRemediationAdvice(vulnType) {
    const advice = {
        'SQL Injection': 'Use parameterized queries and input validation. Consider using ORM frameworks that automatically handle SQL injection protection.',
        'Cross-Site Scripting (XSS)': 'Implement proper input sanitization and output encoding. Use Content Security Policy (CSP) headers.',
        'Security Header Missing': 'Configure proper security headers in your web server configuration.',
        'SSL/TLS Issues': 'Update SSL certificate and configure proper cipher suites.',
        'CORS Misconfiguration': 'Restrict CORS origins to trusted domains only.'
    };
    return advice[vulnType] || 'Implement proper security controls and follow security best practices.';
}

// Added utility functions
function exportReport() {
    alert('📄 PDF export feature coming soon!');
}

function displayCVSSExplanation(score) {
    if (score >= 9) {
        return 'Critical vulnerability, immediate action required!';
    } else if (score >= 7) {
        return 'High vulnerability, recommended to fix soon.';
    } else if (score >= 4) {
        return 'Medium vulnerability, prioritize in the next sprint.';
    } else {
        return 'Low vulnerability, monitor but not urgent.';
    }
}


function scanAgain() {
    document.getElementById('targetUrl').value = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('targetUrl').focus();
}
function resetUI() {
    const button = document.querySelector('button');
    const loading = document.getElementById('loading');

    button.disabled = false;
    button.textContent = 'Start Security Scan';
    loading.style.display = 'none';
}

// Allows Enter key to trigger scan
document.getElementById('targetUrl').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        startScan();
    }
});
