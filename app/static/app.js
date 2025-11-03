// ============================
// AUTH + SCAN FRONTEND LOGIC
// ============================

// --------------------
// Helper Functions
// --------------------

// Get JWT token from storage
function getToken() {
    return localStorage.getItem('token');
}

// Save JWT token
function saveToken(token) {
    localStorage.setItem('token', token);
}

// Remove token (logout)
function clearToken() {
    localStorage.removeItem('token');
}

// --------------------
// Auth Functions
// --------------------

// Register a new user
async function registerUser(email, password, fullName) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Registration failed');
        }

        alert(' Registration successful! You can now log in.');
        document.getElementById('registerForm').reset();
    } catch (error) {
        alert('❌ ' + error.message);
    }
}

// Login and store JWT token
async function loginUser(email, password) {
    try {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Invalid credentials');
        }

        const data = await response.json();
        saveToken(data.access_token);

        showLoggedInState();
        alert(' Logged in successfully!');
    } catch (error) {
        alert(' Login failed: ' + error.message);
    }
}

// Logout function
function logout() {
    clearToken();
    showLoggedOutState();
    alert(' Logged out successfully.');
}

// --------------------
// UI State Handling
// --------------------

function showLoggedInState() {
    document.getElementById('authForms').classList.add('hidden');
    document.getElementById('userInfo').classList.remove('hidden');
    document.getElementById('scannerSection').classList.remove('hidden');
}

function showLoggedOutState() {
    document.getElementById('authForms').classList.remove('hidden');
    document.getElementById('userInfo').classList.add('hidden');
    document.getElementById('scannerSection').classList.add('hidden');
}

// --------------------
// SCAN Logic (Protected Route)
// --------------------

async function startScan() {
    const targetUrl = document.getElementById('targetUrl').value;
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const token = getToken();

    if (!targetUrl) {
        alert('Please enter a website URL');
        return;
    }

    if (!token) {
        alert('You must be logged in to run a scan!');
        return;
    }

    try {
        loading.style.display = 'block';
        results.style.display = 'none';

        const response = await fetch('/api/scan/start', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target_url: targetUrl })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Scan failed');
        }

        resultsContent.innerHTML = `
            <p><strong>Target:</strong> ${data.result.url}</p>
            <p><strong>Status:</strong> ${data.result.status}</p>
            <p><strong>Credits Left:</strong> ${data.credits_left}</p>
            <h4>Vulnerabilities:</h4>
            <ul>${data.result.vulnerabilities.map(v => `<li>${v.type} — Risk: ${v.risk}</li>`).join('')}</ul>
        `;

        results.style.display = 'block';
    } catch (error) {
        alert('❌ ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// --------------------
// EVENT LISTENERS
// --------------------

document.addEventListener('DOMContentLoaded', () => {
    const savedToken = getToken();
    if (savedToken) {
        showLoggedInState();
    } else {
        showLoggedOutState();
    }

    // Login
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        await loginUser(email, password);
    });

    // Register
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        await registerUser(email, password, fullName);
    });

    // Scan
    document.getElementById('scanForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await startScan();
    });
});