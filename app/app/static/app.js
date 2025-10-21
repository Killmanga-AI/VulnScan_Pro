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
        const response = await fetch('/api/scans', {
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

    let html = `
        <div style="margin-bottom: 20px;">
            <h3>Scan Summary</h3>
            <p><strong>Target:</strong> ${data.target_url}</p>
            <p><strong>Vulnerabilities Found:</strong> ${data.vulnerabilities_found}</p>
            <p><strong>Risk Score:</strong> ${data.risk_score}/10</p>
            <p><strong>Status:</strong> ${data.status}</p>
        </div>
    `;

    if (data.vulnerabilities && data.vulnerabilities.length > 0) {
        html += '<h3>Vulnerabilities</h3>';
        data.vulnerabilities.forEach(vuln => {
            html += `
                <div class="vulnerability ${vuln.severity.toLowerCase()}">
                    <h4>${vuln.type} - ${vuln.severity}</h4>
                    <p><strong>Location:</strong> ${vuln.location}</p>
                    <p><strong>Description:</strong> ${vuln.description}</p>
                    <p><strong>CVSS Score:</strong> ${vuln.cvss_score}</p>
                </div>
            `;
        });
    } else {
        html += '<div class="vulnerability low"><p>✅ No vulnerabilities detected. Good job!</p></div>';
    }

    content.innerHTML = html;
    results.style.display = 'block';
}

function resetUI() {
    const button = document.querySelector('button');
    const loading = document.getElementById('loading');

    button.disabled = false;
    button.textContent = 'Start Security Scan';
    loading.style.display = 'none';
}

// Allow Enter key to trigger scan
document.getElementById('targetUrl').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        startScan();
    }
});
