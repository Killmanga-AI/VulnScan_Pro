// ============================
// VulnScan Pro - Frontend JS
// ============================

// --------------------
// Helpers
// --------------------

const TokenKey = 'token';
const UserKey = 'userName';

function getToken() {
    return localStorage.getItem(TokenKey);
}

function saveToken(token) {
    localStorage.setItem(TokenKey, token);
}

function clearToken() {
    localStorage.removeItem(TokenKey);
    localStorage.removeItem(UserKey);
}

function saveUserName(name) {
    localStorage.setItem(UserKey, name);
}

function getUserName() {
    return localStorage.getItem(UserKey);
}

// --------------------
// UI State
// --------------------

function showLoggedInState(userName = '') {
    document.getElementById('authForms').classList.add('hidden');
    document.getElementById('userInfo').classList.remove('hidden');
    document.getElementById('scannerSection').classList.remove('hidden');
    document.getElementById('userEmail').textContent = userName;
}

function showLoggedOutState() {
    document.getElementById('authForms').classList.remove('hidden');
    document.getElementById('userInfo').classList.add('hidden');
    document.getElementById('scannerSection').classList.add('hidden');
}

// --------------------
// Auth Functions
// --------------------

async function registerUser(email, password, fullName) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email.trim(), password: password.trim(), full_name: fullName.trim() })
        });

        if (!response.ok) {
            const text = await response.text();
            console.error('Registration error:', text);
            throw new Error('Registration failed');
        }

        alert('✅ Registration successful! You can now log in.');
        document.getElementById('registerForm').reset();
    } catch (error) {
        alert('❌ ' + error.message);
    }
}

async function loginUser(email, password) {
    try {
        const params = new URLSearchParams();
        params.append('username', email.trim());
        params.append('password', password.trim());

        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params
        });

        if (!response.ok) {
            const text = await response.text();
            console.error('Login error:', text);
            throw new Error('Invalid credentials');
        }

        const data = await response.json();
        saveToken(data.access_token);
        saveUserName(data.full_name || data.email);

        showLoggedInState(data.full_name || data.email);
        alert('✅ Logged in successfully!');
        document.getElementById('loginForm').reset();
    } catch (error) {
        alert('❌ Login failed: ' + error.message);
    }
}

function logout() {
    clearToken();
    showLoggedOutState();
    alert('✅ Logged out successfully.');
}

// --------------------
// Scan Functions
// --------------------

async function startScan() {
    const targetUrl = document.getElementById('targetUrl').value.trim();
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const token = getToken();

    if (!targetUrl) return alert('Please enter a website URL');
    if (!token) return alert('You must be logged in to run a scan!');

    try {
        loading.style.display = 'block';
        results.style.display = 'none';

        const response = await fetch('/api/scan/start', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_url: targetUrl })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Scan failed');

        resultsContent.innerHTML = `
            <p><strong>Target:</strong> ${data.result.url}</p>
            <p><strong>Status:</strong> ${data.result.status}</p>
            <p><strong>Credits Left:</strong> ${data.credits_left}</p>
            <h4>Vulnerabilities:</h4>
            <ul>${data.result.vulnerabilities.map(v => `<li>${v.type} — Risk: ${v.risk}</li>`).join('')}</ul>
        `;

        results.style.display = 'block';
    } catch (error) {
        console.error('Scan error:', error);
        alert('❌ ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// --------------------
// Event Listeners
// --------------------

document.addEventListener('DOMContentLoaded', () => {
    const savedToken = getToken();
    const savedName = getUserName();

    if (savedToken && savedName) showLoggedInState(savedName);
    else showLoggedOutState();

    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await loginUser(
            document.getElementById('loginEmail').value,
            document.getElementById('loginPassword').value
        );
    });

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await registerUser(
            document.getElementById('registerEmail').value,
            document.getElementById('registerPassword').value,
            document.getElementById('registerName').value
        );
    });

    document.getElementById('scanForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await startScan();
    });

    document.getElementById('logoutBtn')?.addEventListener('click', logout);
});
