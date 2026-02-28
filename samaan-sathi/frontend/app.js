// Use API URL from config.js
const API_URL = CONFIG.API_URL;
let accessToken = '';
let currentUser = {};
let inventoryData = [];
let udhaarData = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupNavigation();
    setupUploadArea();
});

// Auth Functions
function checkAuth() {
    const token = localStorage.getItem('accessToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        accessToken = token;
        currentUser = JSON.parse(user);
        console.log('Loaded token from storage');
        showMainApp();
        // Load dashboard data when already logged in
        loadDashboardData();
    } else {
        showAuthScreen();
    }
}

function showAuthScreen() {
    document.getElementById('authScreen').style.display = 'flex';
    document.getElementById('mainApp').style.display = 'none';
}

function showMainApp() {
    document.getElementById('authScreen').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    // Display user's shop name or username if shop name not available
    const displayName = currentUser.shopName || currentUser.username || currentUser.name || 'My Kirana Store';
    document.getElementById('shopName').textContent = displayName;
}

function showAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        tabs[1].classList.add('active');
    }
}

async function register() {
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const fullName = document.getElementById('regFullName').value;
    const shopName = document.getElementById('regShopName').value;
    
    if (!username || !password || !email || !phone || !fullName) {
        showError('registerError', 'All fields are required');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, email, phone, fullName, shopName })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✓ Registration successful! Please login.');
            showAuthTab('login');
        } else {
            showError('registerError', data.error || 'Registration failed');
        }
    } catch (error) {
        showError('registerError', 'Network error: ' + error.message);
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        showError('loginError', 'Username and password required');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        console.log('Login response:', data);
        
        if (response.ok && data.idToken) {
            accessToken = data.idToken;
            
            // Decode JWT to get user attributes
            try {
                const tokenParts = data.idToken.split('.');
                const payload = JSON.parse(atob(tokenParts[1]));
                console.log('Token payload:', payload);
                
                // Extract user info from token
                const shopName = payload['custom:shopName'] || payload.name || username;
                const email = payload.email || '';
                
                currentUser = { 
                    username, 
                    shopName: shopName,
                    email: email,
                    name: payload.name || username
                };
            } catch (e) {
                console.error('Error decoding token:', e);
                // Fallback
                currentUser = { username, shopName: username };
            }
            
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            console.log('✓ Login successful');
            console.log('User:', currentUser);
            console.log('Token saved (first 50 chars):', accessToken.substring(0, 50) + '...');
            console.log('Token length:', accessToken.length);
            
            showMainApp();
            // Load dashboard data after login
            loadDashboardData();
        } else {
            showError('loginError', data.error || 'Login failed');
        }
    } catch (error) {
        showError('loginError', 'Network error: ' + error.message);
    }
}

function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('currentUser');
    accessToken = '';
    currentUser = {};
    console.log('Logged out');
    showAuthScreen();
}

function showForgotPassword() {
    // Reset form
    document.getElementById('resetUsername').value = '';
    document.getElementById('resetEmail').value = '';
    document.getElementById('resetNewPassword').value = '';
    document.getElementById('resetConfirmPassword').value = '';
    document.getElementById('resetPasswordError').textContent = '';
    
    // Open modal using active class (consistent with other modals)
    document.getElementById('forgotPasswordModal').classList.add('active');
}

async function simpleResetPassword() {
    const username = document.getElementById('resetUsername').value.trim();
    const email = document.getElementById('resetEmail').value.trim();
    const newPassword = document.getElementById('resetNewPassword').value;
    const confirmPassword = document.getElementById('resetConfirmPassword').value;
    
    // Validation
    if (!username || !email || !newPassword || !confirmPassword) {
        showError('resetPasswordError', 'All fields are required');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showError('resetPasswordError', 'Passwords do not match');
        return;
    }
    
    if (newPassword.length < 8) {
        showError('resetPasswordError', 'Password must be at least 8 characters');
        return;
    }
    
    try {
        console.log('Attempting password reset for:', username);
        console.log('API URL:', API_URL);
        
        // Use register endpoint with special action flag (workaround for missing API Gateway route)
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ 
                _action: 'reset-password',
                username, 
                email,
                newPassword 
            })
        });
        
        console.log('Response status:', response.status);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            alert('✓ Password reset successful! You can now login with your new password.');
            closeModal('forgotPasswordModal');
            showAuthTab('login');
            // Pre-fill username
            document.getElementById('loginUsername').value = username;
        } else {
            showError('resetPasswordError', data.error || 'Failed to reset password');
        }
    } catch (error) {
        console.error('Reset password error:', error);
        showError('resetPasswordError', 'Failed to reset password. Please try again or contact administrator.');
    }
}

function showError(elementId, message) {
    document.getElementById(elementId).textContent = message;
    setTimeout(() => {
        document.getElementById(elementId).textContent = '';
    }, 5000);
}

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            showPage(page);
            
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`${pageName}Page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Load page data
        switch(pageName) {
            case 'dashboard':
                loadDashboardData();
                break;
            case 'inventory':
                loadInventoryData();
                break;
            case 'udhaar':
                loadUdhaarData();
                break;
            case 'forecast':
                initForecast();
                break;
            case 'pricing':
                initPricing();
                break;
        }
    }
}

// Dashboard
function initDashboard() {
    document.getElementById('totalItems').textContent = '-';
    document.getElementById('lowStockItems').textContent = '-';
    document.getElementById('totalUdhaar').textContent = '₹0';
    document.getElementById('activeAlerts').textContent = '-';
    
    const alertsContainer = document.getElementById('dashboardAlerts');
    alertsContainer.innerHTML = '<p class="loading">Dashboard ready. Use other sections to add data.</p>';
    
    const recsContainer = document.getElementById('dashboardRecommendations');
    recsContainer.innerHTML = '<p class="loading">Add inventory items to get recommendations.</p>';
}

// Inventory
function initInventory() {
    const container = document.getElementById('inventoryList');
    container.innerHTML = '<p class="loading">No items yet. Click "+ Add Item" to get started!</p>';
}

function showAddItemModal() {
    document.getElementById('addItemModal').classList.add('active');
}

// Udhaar
function initUdhaar() {
    document.getElementById('udhaarTotal').textContent = '₹0';
    document.getElementById('udhaarCustomers').textContent = '0';
    document.getElementById('udhaarOverdue').textContent = '0';
    
    const container = document.getElementById('udhaarList');
    container.innerHTML = '<p class="loading">No udhaar records yet. Click "+ Add Udhaar" to start.</p>';
}

function filterUdhaar() {
    const status = document.getElementById('udhaarStatusFilter').value;
    
    const items = document.querySelectorAll('.udhaar-item');
    items.forEach(item => {
        const itemStatus = item.querySelector('.status')?.textContent || '';
        item.style.display = !status || itemStatus === status ? 'flex' : 'none';
    });
}

function showAddUdhaarModal() {
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('udhaarDueDate').setAttribute('min', today);
    document.getElementById('addUdhaarModal').classList.add('active');
}

function showPaymentModal(customerId, customerName, outstanding) {
    document.getElementById('paymentCustomerId').value = customerId;
    document.getElementById('paymentCustomerName').textContent = customerName;
    document.getElementById('paymentOutstanding').textContent = `₹${outstanding}`;
    document.getElementById('paymentModal').classList.add('active');
}

async function recordPayment() {
    const customerId = document.getElementById('paymentCustomerId').value;
    const amount = parseFloat(document.getElementById('paymentAmount').value) || 0;
    
    if (!amount || amount <= 0) {
        alert('⚠️ Please enter valid payment amount');
        return;
    }
    
    try {
        console.log('Recording payment:', { customerId, amount });
        const response = await apiPost('/udhaar/payment', { customerId, amount });
        console.log('Payment recorded:', response);
        
        alert('✓ Payment recorded successfully!');
        closeModal('paymentModal');
        document.getElementById('paymentAmount').value = '';
        
        // Reload udhaar data to show updated information
        loadUdhaarData();
        
    } catch (error) {
        console.error('Failed to record payment:', error);
        alert('❌ Failed to record payment: ' + error.message);
    }
}

// Forecast
function initForecast() {
    const container = document.getElementById('forecastList');
    container.innerHTML = '<p class="loading">Select items and click "Generate Forecast".</p>';
    
    // Load items into checkboxes
    loadForecastItemsCheckboxes();
}

async function loadForecastItemsCheckboxes() {
    try {
        const response = await apiGet('/inventory');
        const items = response.items || [];
        
        const container = document.getElementById('forecastItemCheckboxes');
        
        if (items.length === 0) {
            container.innerHTML = '<p style="color: #666;">No items available. Add items first.</p>';
            return;
        }
        
        container.innerHTML = items.map(item => `
            <label style="display: block; padding: 0.5rem; cursor: pointer; border-bottom: 1px solid #eee;">
                <input type="checkbox" value="${item.itemId}" data-name="${item.name}" style="margin-right: 0.5rem;">
                ${item.name} <span style="color: #666; font-size: 0.9rem;">(${item.itemId})</span>
            </label>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load items for forecast:', error);
        const container = document.getElementById('forecastItemCheckboxes');
        container.innerHTML = '<p style="color: red;">Failed to load items</p>';
    }
}

async function generateForecast() {
    const checkboxes = document.querySelectorAll('#forecastItemCheckboxes input[type="checkbox"]:checked');
    const days = parseInt(document.getElementById('forecastDays').value) || 7;
    
    if (checkboxes.length === 0) {
        alert('⚠️ Please select at least one item');
        return;
    }
    
    const itemIdArray = Array.from(checkboxes).map(cb => cb.value);
    const itemNames = Array.from(checkboxes).map(cb => cb.dataset.name);
    
    try {
        console.log('Generating forecast for:', itemIdArray);
        const response = await apiPost('/forecast/demand', { 
            itemIds: itemIdArray, 
            days: days 
        });
        console.log('Forecast generated:', response);
        
        // Add item names to forecast data
        response.forecasts.forEach((forecast, index) => {
            forecast.itemName = itemNames[index] || forecast.itemId;
        });
        
        alert('✓ Forecast generated successfully!');
        displayForecast(response.forecasts || []);
        
    } catch (error) {
        console.error('Failed to generate forecast:', error);
        alert('❌ Failed to generate forecast: ' + error.message);
    }
}

function displayForecast(forecasts) {
    const container = document.getElementById('forecastList');
    
    if (!forecasts || forecasts.length === 0) {
        container.innerHTML = '<p class="loading">No forecast data available.</p>';
        return;
    }
    
    container.innerHTML = forecasts.map(forecast => `
        <div class="forecast-item">
            <h4>${forecast.itemName || 'Unknown Item'}</h4>
            <p style="color: #666; font-size: 0.9rem;">Item ID: ${forecast.itemId}</p>
            <div class="forecast-chart">
                ${(forecast.forecast || []).slice(0, 7).map(day => `
                    <div class="forecast-day">
                        <div class="date">${new Date(day.date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}</div>
                        <div class="quantity">${day.predictedQuantity || 0}</div>
                    </div>
                `).join('')}
            </div>
            <div class="forecast-recommendation">
                📊 ${forecast.recommendation || 'No recommendation available'}
            </div>
            <p style="margin-top: 1rem; color: #666;">
                Confidence: ${((forecast.confidence || 0) * 100).toFixed(0)}%
            </p>
        </div>
    `).join('');
}

// Pricing
function initPricing() {
    const container = document.getElementById('pricingList');
    container.innerHTML = '<p class="loading">No pricing recommendations available. Click "Get Recommendations" to generate.</p>';
}

async function getPricingRecommendations() {
    try {
        console.log('Getting pricing recommendations...');
        const response = await apiGet('/pricing/recommendations');
        console.log('Pricing recommendations:', response);
        
        displayPricing(response.recommendations || []);
        
    } catch (error) {
        console.error('Failed to get pricing recommendations:', error);
        alert('❌ Failed to get pricing recommendations: ' + error.message);
    }
}

function displayPricing(recommendations) {
    const container = document.getElementById('pricingList');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p class="loading">No pricing recommendations available.</p>';
        return;
    }
    
    container.innerHTML = recommendations.map(rec => `
        <div class="pricing-item">
            <h4>${rec.itemName || 'Unknown Item'}</h4>
            <div class="pricing-comparison">
                <div class="price-box current">
                    <div class="label">Current Price</div>
                    <div class="price">₹${rec.currentPrice || 0}</div>
                    <div class="label">${rec.currentMargin || 0}% margin</div>
                </div>
                <div class="price-box suggested">
                    <div class="label">Suggested Price</div>
                    <div class="price">₹${rec.suggestedPrice || 0}</div>
                    <div class="label">${rec.suggestedMargin || 0}% margin</div>
                </div>
            </div>
            <div class="pricing-action ${rec.action || 'MAINTAIN'}">
                ${rec.action === 'INCREASE' ? '📈' : rec.action === 'DECREASE' ? '📉' : '➡️'} 
                ${rec.action || 'MAINTAIN'}
            </div>
            <div class="pricing-reason">
                ${rec.reason || 'No reason provided'}
            </div>
        </div>
    `).join('');
}

// OCR
function setupUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    
    if (!uploadArea) return;
    
    uploadArea.addEventListener('click', () => {
        document.getElementById('billImage').click();
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border)';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            processImageFile(file);
        }
    });
}

async function processBill() {
    const fileInput = document.getElementById('billImage');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('⚠️ Please select an image file');
        return;
    }
    
    await processImageFile(file);
}

async function processImageFile(file) {
    try {
        console.log('Processing image:', file.name);
        
        // Convert to base64
        const base64 = await fileToBase64(file);
        
        // Store for later use
        window.lastImageBase64 = base64;
        
        // Show loading
        const resultDiv = document.getElementById('ocrResult');
        resultDiv.innerHTML = '<p class="loading">📸 Processing image...</p>';
        resultDiv.style.display = 'block';
        
        // Call OCR API (without saveToSales initially)
        const response = await apiPost('/ocr/process', { imageBase64: base64 });
        console.log('OCR result:', response);
        
        displayOCRResult(response);
        
    } catch (error) {
        console.error('Failed to process image:', error);
        alert('❌ Failed to process image: ' + error.message);
    }
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function displayOCRResult(data) {
    const container = document.getElementById('ocrResult');
    const structured = data.structuredData || {};
    
    container.innerHTML = `
        <h3>✓ Extracted Data</h3>
        <div class="ocr-data">
            <div class="ocr-field">
                <strong>Vendor:</strong> ${structured.vendor || 'N/A'}
            </div>
            <div class="ocr-field">
                <strong>Date:</strong> ${structured.date || 'N/A'}
            </div>
            <div class="ocr-field">
                <strong>Total:</strong> ₹${structured.total || 0}
            </div>
            <div class="ocr-field">
                <strong>Confidence:</strong> ${((data.confidence || 0) * 100).toFixed(1)}%
            </div>
        </div>
        ${structured.items && structured.items.length > 0 ? `
            <div class="ocr-items">
                <h4>Items Detected:</h4>
                ${structured.items.map(item => `
                    <div class="ocr-item">
                        <span>${item.name || 'Unknown'}</span>
                        <span>${item.quantity || 1} × ₹${item.price || 0}</span>
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
                <button class="btn-primary" onclick="addBillToInventory()">
                    ➕ Add to Inventory
                </button>
                <button class="btn-secondary" onclick="document.getElementById('ocrResult').style.display='none'">
                    ✕ Close
                </button>
            </div>
            <p style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                💡 This will add new items or increase quantities of existing items in your inventory.
            </p>
        ` : ''}
    `;
    
    // Store the data for later use
    window.lastOCRData = data;
}

async function addBillToInventory() {
    if (!window.lastOCRData) {
        alert('⚠️ No OCR data available');
        return;
    }
    
    try {
        console.log('Adding bill items to inventory...');
        
        // Re-process with addToInventory flag
        const imageBase64 = window.lastImageBase64;
        if (!imageBase64) {
            alert('⚠️ Image data not available. Please scan again.');
            return;
        }
        
        const response = await apiPost('/ocr/process', { 
            imageBase64: imageBase64,
            addToInventory: true
        });
        
        console.log('Add to inventory response:', response);
        
        if (response.inventoryResult && response.inventoryResult.success) {
            const result = response.inventoryResult;
            let message = '✓ Items added to inventory successfully!\n\n';
            
            if (result.added > 0) {
                message += `📦 New items added: ${result.added}\n`;
                result.addedItems.forEach(item => {
                    message += `  • ${item.name}: ${item.quantity} units @ ₹${item.price}\n`;
                });
            }
            
            if (result.updated > 0) {
                message += `\n🔄 Existing items updated: ${result.updated}\n`;
                result.updatedItems.forEach(item => {
                    message += `  • ${item.name}: ${item.oldQuantity} → ${item.newQuantity} (+${item.added})\n`;
                });
            }
            
            alert(message);
            
            // Reload inventory if on inventory page
            if (document.getElementById('inventoryPage').classList.contains('active')) {
                await loadInventoryData();
            }
            
            // Close OCR result
            document.getElementById('ocrResult').style.display = 'none';
        } else {
            const errorMsg = response.inventoryResult?.message || 'Unknown error';
            alert('⚠️ Failed to add items to inventory: ' + errorMsg);
        }
        
    } catch (error) {
        console.error('Failed to add bill to inventory:', error);
        alert('❌ Failed to add items: ' + error.message);
    }
}

// API Helper Functions
async function apiGet(endpoint) {
    // Ensure we have token
    if (!accessToken) {
        accessToken = localStorage.getItem('accessToken') || '';
    }
    
    if (!accessToken) {
        throw new Error('Not authenticated. Please login.');
    }
    
    console.log('GET Request:', endpoint);
    console.log('Token (first 30):', accessToken.substring(0, 30) + '...');
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
        let errorMsg = `API Error: ${response.status}`;
        try {
            const error = await response.json();
            errorMsg = error.error || error.message || errorMsg;
        } catch (e) {
            const text = await response.text();
            errorMsg = text || errorMsg;
        }
        console.error('API Error:', errorMsg);
        throw new Error(errorMsg);
    }
    
    const result = await response.json();
    console.log('Response:', result);
    return result;
}

async function apiPost(endpoint, data) {
    // Ensure we have token
    if (!accessToken) {
        accessToken = localStorage.getItem('accessToken') || '';
    }
    
    if (!accessToken) {
        throw new Error('Not authenticated. Please login.');
    }
    
    console.log('POST Request:', endpoint);
    console.log('Data:', data);
    console.log('Token (first 30):', accessToken.substring(0, 30) + '...');
    console.log('Token length:', accessToken.length);
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
        let errorMsg = `API Error: ${response.status}`;
        try {
            const error = await response.json();
            errorMsg = error.error || error.message || errorMsg;
        } catch (e) {
            const text = await response.text();
            errorMsg = text || errorMsg;
        }
        console.error('API Error:', errorMsg);
        throw new Error(errorMsg);
    }
    
    const result = await response.json();
    console.log('Response:', result);
    return result;
}

// Modal Functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    
    // Reset edit state when closing add item modal
    if (modalId === 'addItemModal' && editingItemId) {
        editingItemId = null;
        document.querySelector('#addItemModal .modal-header h3').textContent = 'Add Inventory Item';
        const submitBtn = document.querySelector('#addItemModal button[onclick="addInventoryItem()"]');
        if (submitBtn) {
            submitBtn.textContent = '➕ Add Item';
        }
        
        // Clear form
        document.getElementById('itemName').value = '';
        document.getElementById('itemCategory').value = 'groceries';
        document.getElementById('itemQuantity').value = '';
        document.getElementById('itemUnit').value = 'pcs';
        document.getElementById('itemCostPrice').value = '';
        document.getElementById('itemSellingPrice').value = '';
        document.getElementById('itemMinStock').value = '10';
        document.getElementById('itemExpiryDate').value = '';
    }
}

// Close modal on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}


// ==================== LOAD DATA FUNCTIONS ====================
async function loadInventoryData() {
    try {
        console.log('Loading inventory data...');
        const response = await apiGet('/inventory');
        inventoryData = response.items || [];
        console.log('Loaded inventory items:', inventoryData.length);
        displayInventory(inventoryData);
        return inventoryData;
    } catch (error) {
        console.error('Failed to load inventory:', error);
        inventoryData = [];
        displayInventory([]);
        return [];
    }
}

async function loadUdhaarData() {
    try {
        console.log('Loading udhaar data...');
        const response = await apiGet('/udhaar');
        udhaarData = response.records || [];
        console.log('Loaded udhaar records:', udhaarData.length);
        
        // Update summary
        if (response.summary) {
            document.getElementById('udhaarTotal').textContent = `₹${response.summary.totalOutstanding || 0}`;
            document.getElementById('udhaarCustomers').textContent = response.summary.totalCustomers || 0;
            document.getElementById('udhaarOverdue').textContent = response.summary.overdueCount || 0;
        }
        
        displayUdhaar(udhaarData);
        return udhaarData;
    } catch (error) {
        console.error('Failed to load udhaar:', error);
        udhaarData = [];
        displayUdhaar([]);
        return [];
    }
}

async function loadDashboardData() {
    try {
        // Load all data
        const [inventory, udhaar, recommendations] = await Promise.all([
            loadInventoryData().catch(() => []),
            loadUdhaarData().catch(() => []),
            apiGet('/recommendations').catch(() => ({ recommendations: [] }))
        ]);
        
        // Update dashboard stats
        document.getElementById('totalItems').textContent = inventory.length || 0;
        
        const lowStockItems = inventory.filter(item => 
            (item.quantity || 0) < (item.minStockLevel || 10)
        );
        document.getElementById('lowStockItems').textContent = lowStockItems.length;
        
        const totalUdhaar = udhaar.reduce((sum, r) => sum + (parseFloat(r.outstandingAmount) || 0), 0);
        document.getElementById('totalUdhaar').textContent = `₹${totalUdhaar.toFixed(0)}`;
        
        // Count alerts
        const today = new Date();
        const expiringItems = inventory.filter(item => {
            if (!item.expiryDate) return false;
            const expiry = new Date(item.expiryDate);
            const daysToExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
            return daysToExpiry <= 30 && daysToExpiry >= 0;
        });
        
        const expiredItems = inventory.filter(item => {
            if (!item.expiryDate) return false;
            const expiry = new Date(item.expiryDate);
            return expiry < today;
        });
        
        const overdueUdhaar = udhaar.filter(r => r.status === 'OVERDUE');
        
        const totalAlerts = lowStockItems.length + expiringItems.length + expiredItems.length + overdueUdhaar.length;
        document.getElementById('activeAlerts').textContent = totalAlerts;
        
        // Display recommendations
        displayDashboardRecommendations(recommendations.recommendations || []);
        
        // Display alerts
        const alerts = [];
        
        // Expired items - CRITICAL
        if (expiredItems.length > 0) {
            const itemNames = expiredItems.slice(0, 3).map(item => item.name).join(', ');
            const moreText = expiredItems.length > 3 ? ` and ${expiredItems.length - 3} more` : '';
            alerts.push({
                priority: 'high',
                title: '🚨 EXPIRED Items',
                message: `${expiredItems.length} items have expired: ${itemNames}${moreText}`,
                action: 'Remove from shelves immediately to avoid health risks'
            });
        }
        
        // Expiring soon - HIGH
        if (expiringItems.length > 0) {
            const itemNames = expiringItems.slice(0, 3).map(item => item.name).join(', ');
            const moreText = expiringItems.length > 3 ? ` and ${expiringItems.length - 3} more` : '';
            alerts.push({
                priority: 'high',
                title: '⚠️ Items Expiring Soon',
                message: `${expiringItems.length} items expiring within 30 days: ${itemNames}${moreText}`,
                action: 'Offer discounts or combo deals to clear stock before expiry'
            });
        }
        
        // Low stock - HIGH
        if (lowStockItems.length > 0) {
            const itemNames = lowStockItems.slice(0, 3).map(item => item.name).join(', ');
            const moreText = lowStockItems.length > 3 ? ` and ${lowStockItems.length - 3} more` : '';
            alerts.push({
                priority: 'high',
                title: '⚠️ Low Stock Alert',
                message: `${lowStockItems.length} items running low: ${itemNames}${moreText}`,
                action: 'Restock immediately to avoid stock-outs'
            });
        }
        
        // Overdue udhaar - MEDIUM
        if (overdueUdhaar.length > 0) {
            const overdueAmount = overdueUdhaar.reduce((sum, r) => sum + parseFloat(r.outstandingAmount || 0), 0);
            alerts.push({
                priority: 'medium',
                title: '💳 Overdue Payments',
                message: `${overdueUdhaar.length} customers have overdue payments totaling ₹${overdueAmount.toFixed(0)}`,
                action: 'Send payment reminders to improve cash flow'
            });
        }
        
        // High total udhaar - MEDIUM
        if (totalUdhaar > 5000 && overdueUdhaar.length === 0) {
            alerts.push({
                priority: 'medium',
                title: '💰 Outstanding Credit',
                message: `₹${totalUdhaar.toFixed(0)} pending from customers`,
                action: 'Follow up with customers for payment'
            });
        }
        
        // All good
        if (alerts.length === 0) {
            alerts.push({
                priority: 'low',
                title: '✅ All Good',
                message: 'Your shop is running smoothly!',
                action: ''
            });
        }
        
        displayDashboardAlerts(alerts);
        
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

function displayDashboardAlerts(alerts) {
    const container = document.getElementById('dashboardAlerts');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p class="loading">No alerts at this time. Your shop is running smoothly!</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item ${alert.priority}" style="${alert.priority === 'high' ? 'background-color: #fee; border-left: 4px solid #e53e3e;' : ''}">
            <h4>${alert.title}</h4>
            <p>${alert.message}</p>
            ${alert.action ? `<p><strong>Action:</strong> ${alert.action}</p>` : ''}
        </div>
    `).join('');
}

function displayDashboardRecommendations(recommendations) {
    const container = document.getElementById('dashboardRecommendations');
    
    if (!recommendations || recommendations.length === 0) {
        // Generate simple recommendations based on current data
        const simpleRecs = generateSimpleRecommendations();
        if (simpleRecs.length > 0) {
            container.innerHTML = simpleRecs.map(rec => `
                <div class="recommendation-item">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                    ${rec.impact ? `<p class="impact">💡 ${rec.impact}</p>` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="loading">Add inventory and udhaar data to get personalized recommendations.</p>';
        }
        return;
    }
    
    container.innerHTML = recommendations.slice(0, 3).map(rec => `
        <div class="recommendation-item">
            <h4>${rec.title}</h4>
            <p>${rec.description}</p>
            ${rec.expectedImpact ? `<p class="impact">💡 ${rec.expectedImpact}</p>` : ''}
        </div>
    `).join('');
}

function generateSimpleRecommendations() {
    const recs = [];
    
    // Check inventory
    if (inventoryData.length > 0) {
        const lowStockItems = inventoryData.filter(item => 
            (item.quantity || 0) < (item.minStockLevel || 10)
        );
        
        if (lowStockItems.length > 0) {
            recs.push({
                title: '📦 Restock Low Items',
                description: `You have ${lowStockItems.length} items running low. Order stock for ${lowStockItems.slice(0, 2).map(i => i.name).join(', ')}${lowStockItems.length > 2 ? ' and others' : ''} to avoid running out.`,
                impact: 'Prevents lost sales and keeps customers happy'
            });
        }
        
        // Check high margin items
        const highMarginItems = inventoryData.filter(item => {
            const margin = ((item.sellingPrice - item.costPrice) / item.sellingPrice) * 100;
            return margin > 35 && item.quantity > item.minStockLevel;
        });
        
        if (highMarginItems.length > 0) {
            recs.push({
                title: '💰 Promote High Profit Items',
                description: `Items like ${highMarginItems.slice(0, 2).map(i => i.name).join(', ')} have good profit margins. Display them prominently to increase sales.`,
                impact: 'Increases your daily profit'
            });
        }
    }
    
    // Check udhaar
    if (udhaarData.length > 0) {
        const totalOutstanding = udhaarData.reduce((sum, r) => sum + (parseFloat(r.outstandingAmount) || 0), 0);
        const overdueRecords = udhaarData.filter(r => r.status === 'OVERDUE');
        
        if (overdueRecords.length > 0) {
            recs.push({
                title: '💳 Follow Up on Overdue Payments',
                description: `${overdueRecords.length} customers have overdue payments totaling ₹${overdueRecords.reduce((sum, r) => sum + parseFloat(r.outstandingAmount || 0), 0).toFixed(0)}. Send friendly reminders to collect payments.`,
                impact: 'Improves cash flow for your business'
            });
        } else if (totalOutstanding > 3000) {
            recs.push({
                title: '💵 Manage Credit Wisely',
                description: `You have ₹${totalOutstanding.toFixed(0)} in outstanding credit. Consider setting credit limits per customer to manage risk.`,
                impact: 'Protects your business from bad debts'
            });
        }
    }
    
    // General tips
    if (recs.length === 0) {
        recs.push({
            title: '✅ Everything Looks Good!',
            description: 'Your shop is running smoothly. Keep tracking your inventory and credit to stay on top of your business.',
            impact: 'Consistent monitoring leads to better profits'
        });
    }
    
    return recs;
}

// Display inventory items
function displayInventory(items) {
    // Don't overwrite inventoryData - just display the filtered items
    const container = document.getElementById('inventoryList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<p class="loading">No items yet. Click "+ Add Item" to get started!</p>';
        return;
    }
    
    container.innerHTML = items.map(item => {
        const isLowStock = (item.quantity || 0) < (item.minStockLevel || 10);
        const margin = (((item.sellingPrice || 0) - (item.costPrice || 0)) / (item.sellingPrice || 1) * 100).toFixed(1);
        
        // Check expiry
        const expiryDate = item.expiryDate ? new Date(item.expiryDate) : null;
        const today = new Date();
        const daysToExpiry = expiryDate ? Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24)) : null;
        let expiryWarning = '';
        
        if (daysToExpiry !== null) {
            if (daysToExpiry < 0) {
                expiryWarning = '<div class="expiry-warning expired">⚠️ EXPIRED</div>';
            } else if (daysToExpiry <= 7) {
                expiryWarning = `<div class="expiry-warning near-expiry">⚠️ Expires in ${daysToExpiry} days</div>`;
            } else if (daysToExpiry <= 30) {
                expiryWarning = `<div class="expiry-warning">Expires in ${daysToExpiry} days</div>`;
            }
        }
        
        return `
            <div class="inventory-item" data-category="${item.category || 'uncategorized'}">
                <div class="item-header">
                    <h4>${item.name}</h4>
                    <div class="item-menu">
                        <button class="menu-btn" onclick="toggleItemMenu(event, '${item.itemId}')">⋮</button>
                        <div class="menu-dropdown" id="menu-${item.itemId}">
                            <button onclick='editInventoryItem(${JSON.stringify(item).replace(/'/g, "&apos;")})'>✏️ Edit</button>
                            <button onclick="deleteInventoryItem('${item.itemId}', '${item.name}')">🗑️ Delete</button>
                        </div>
                    </div>
                </div>
                <span class="category">${item.category || 'Uncategorized'}</span>
                ${expiryWarning}
                <div class="details">
                    <div class="detail"><strong>Quantity:</strong> ${item.quantity || 0} ${item.unit || 'pcs'}</div>
                    <div class="detail"><strong>Min Stock:</strong> ${item.minStockLevel || 10} ${item.unit || 'pcs'}</div>
                    ${item.expiryDate ? `<div class="detail"><strong>Expiry:</strong> ${new Date(item.expiryDate).toLocaleDateString()}</div>` : ''}
                    <div class="detail"><strong>Cost:</strong> ₹${item.costPrice || 0}</div>
                    <div class="detail"><strong>Price:</strong> ₹${item.sellingPrice || 0}</div>
                    <div class="detail"><strong>Margin:</strong> ${margin}%</div>
                </div>
                <div class="stock-status ${isLowStock ? 'low' : 'good'}">
                    ${isLowStock ? '⚠️ Low Stock' : '✓ In Stock'}
                </div>
            </div>
        `;
    }).join('');
}

function toggleItemMenu(event, itemId) {
    event.stopPropagation();
    
    // Close all other menus
    document.querySelectorAll('.menu-dropdown').forEach(menu => {
        if (menu.id !== `menu-${itemId}`) {
            menu.classList.remove('active');
        }
    });
    
    // Toggle current menu
    const menu = document.getElementById(`menu-${itemId}`);
    menu.classList.toggle('active');
}

// Close menus when clicking outside
document.addEventListener('click', (event) => {
    if (!event.target.closest('.item-menu')) {
        document.querySelectorAll('.menu-dropdown').forEach(menu => {
            menu.classList.remove('active');
        });
    }
});

// Display udhaar records
function displayUdhaar(records) {
    // Don't overwrite udhaarData - just display the filtered records
    const container = document.getElementById('udhaarList');
    
    if (!records || records.length === 0) {
        container.innerHTML = '<p class="loading">No udhaar records yet. Click "+ Add Udhaar" to start tracking credit.</p>';
        return;
    }
    
    container.innerHTML = records.map(record => `
        <div class="udhaar-item" data-status="${record.status || 'pending'}">
            <div class="udhaar-info">
                <h4>${record.customerName}</h4>
                <p>Customer ID: ${record.customerId}</p>
                <p>Last Updated: ${new Date(record.lastUpdated).toLocaleDateString()}</p>
                <div class="udhaar-actions">
                    <button class="btn-small btn-success" 
                        onclick="showPaymentModal('${record.customerId}', '${record.customerName}', ${record.outstandingAmount})">
                        Record Payment
                    </button>
                </div>
            </div>
            <div class="udhaar-amount">
                <div class="amount">₹${record.outstandingAmount || 0}</div>
                <span class="status ${record.status || 'pending'}">${record.status || 'PENDING'}</span>
            </div>
        </div>
    `).join('');
}

// Update showPage to load data
// Filter functions work with loaded data
function filterInventory() {
    const search = document.getElementById('searchInventory').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value;
    
    console.log('Filtering inventory - Search:', search, 'Category:', category);
    console.log('Total items:', inventoryData.length);
    
    let filtered = inventoryData;
    
    if (search) {
        filtered = filtered.filter(item => 
            (item.name || '').toLowerCase().includes(search) ||
            (item.itemId || '').toLowerCase().includes(search) ||
            (item.category || '').toLowerCase().includes(search)
        );
    }
    
    if (category) {
        filtered = filtered.filter(item => item.category === category);
    }
    
    console.log('Filtered items:', filtered.length);
    displayInventory(filtered);
}

// Filter udhaar records by status and search
function filterUdhaar() {
    const search = document.getElementById('searchUdhaar').value.toLowerCase();
    const status = document.getElementById('udhaarStatusFilter').value;
    
    console.log('Filtering udhaar - Search:', search, 'Status:', status);
    console.log('Total records:', udhaarData.length);
    
    let filtered = udhaarData;
    
    // Filter by search
    if (search) {
        filtered = filtered.filter(record => 
            (record.customerName || '').toLowerCase().includes(search) ||
            (record.customerId || '').toLowerCase().includes(search)
        );
    }
    
    // Filter by status
    if (status) {
        filtered = filtered.filter(record => 
            (record.status || 'PENDING').toUpperCase() === status.toUpperCase()
        );
    }
    
    console.log('Filtered records:', filtered.length);
    displayUdhaar(filtered);
}

// Add item function with data reload
async function addInventoryItem() {
    const name = document.getElementById('itemName').value.trim();
    const category = document.getElementById('itemCategory').value;
    const quantity = parseInt(document.getElementById('itemQuantity').value) || 0;
    const unit = document.getElementById('itemUnit').value;
    const costPrice = parseFloat(document.getElementById('itemCostPrice').value) || 0;
    const sellingPrice = parseFloat(document.getElementById('itemSellingPrice').value) || 0;
    const minStockLevel = parseInt(document.getElementById('itemMinStock').value) || 10;
    const expiryDate = document.getElementById('itemExpiryDate').value || null;
    
    if (!name || !category) {
        alert('⚠️ Please fill all required fields (Item Name, Category)');
        return;
    }
    
    // If editing existing item
    if (editingItemId) {
        const item = {
            itemId: editingItemId,
            name: name,
            category: category,
            quantity: quantity,
            unit: unit,
            costPrice: costPrice,
            sellingPrice: sellingPrice,
            minStockLevel: minStockLevel,
            expiryDate: expiryDate
        };
        
        try {
            console.log('Updating inventory item:', item);
            const response = await apiPost('/inventory', item);
            console.log('Item updated successfully:', response);
            
            alert('✓ Item updated successfully!');
            closeModal('addItemModal');
            
            // Reset editing state
            editingItemId = null;
            document.querySelector('#addItemModal .modal-header h3').textContent = 'Add Inventory Item';
            const submitBtn = document.querySelector('#addItemModal button[onclick="addInventoryItem()"]');
            if (submitBtn) {
                submitBtn.textContent = '➕ Add Item';
            }
            
            // Clear form
            document.getElementById('itemName').value = '';
            document.getElementById('itemCategory').value = 'groceries';
            document.getElementById('itemQuantity').value = '';
            document.getElementById('itemUnit').value = 'pcs';
            document.getElementById('itemCostPrice').value = '';
            document.getElementById('itemSellingPrice').value = '';
            document.getElementById('itemMinStock').value = '10';
            document.getElementById('itemExpiryDate').value = '';
            
            // Reload inventory
            await loadInventoryData();
            
            return;
        } catch (error) {
            console.error('Failed to update item:', error);
            alert('❌ Failed to update item: ' + error.message);
            return;
        }
    }
    
    // Check for duplicate item name (only when adding new)
    const duplicate = inventoryData.find(item => 
        item.name.toLowerCase() === name.toLowerCase()
    );
    
    if (duplicate) {
        const newQuantity = duplicate.quantity + quantity;
        const updateQuantity = confirm(
            `⚠️ "${name}" already exists!\n\n` +
            `Current Quantity: ${duplicate.quantity} ${duplicate.unit}\n` +
            `Adding: ${quantity} ${unit}\n` +
            `New Total: ${newQuantity} ${unit}\n\n` +
            `Click OK to update the quantity, or Cancel to abort.`
        );
        
        if (!updateQuantity) {
            return;
        }
        
        // Update existing item
        try {
            const updatedItem = {
                itemId: duplicate.itemId,
                name: duplicate.name,
                category: duplicate.category,
                quantity: newQuantity,
                unit: duplicate.unit,
                costPrice: duplicate.costPrice,
                sellingPrice: duplicate.sellingPrice,
                minStockLevel: duplicate.minStockLevel,
                expiryDate: duplicate.expiryDate
            };
            
            console.log('Updating inventory item:', updatedItem);
            const response = await apiPost('/inventory', updatedItem);
            console.log('Item updated successfully:', response);
            
            alert(`✓ Item quantity updated!\n\nOld: ${duplicate.quantity} ${duplicate.unit}\nNew: ${newQuantity} ${unit}`);
            closeModal('addItemModal');
            
            // Clear form
            document.getElementById('itemName').value = '';
            document.getElementById('itemCategory').value = 'groceries';
            document.getElementById('itemQuantity').value = '';
            document.getElementById('itemUnit').value = 'pcs';
            document.getElementById('itemCostPrice').value = '';
            document.getElementById('itemSellingPrice').value = '';
            document.getElementById('itemMinStock').value = '10';
            document.getElementById('itemExpiryDate').value = '';
            
            // Reload inventory
            await loadInventoryData();
            
            return;
        } catch (error) {
            console.error('Failed to update item:', error);
            alert('❌ Failed to update item: ' + error.message);
            return;
        }
    }
    
    // Auto-generate item ID for new item
    const itemId = 'ITEM-' + Date.now();
    
    const item = {
        itemId: itemId,
        name: name,
        category: category,
        quantity: quantity,
        unit: unit,
        costPrice: costPrice,
        sellingPrice: sellingPrice,
        minStockLevel: minStockLevel,
        expiryDate: expiryDate
    };
    
    try {
        console.log('Adding inventory item:', item);
        const response = await apiPost('/inventory', item);
        console.log('Item added successfully:', response);
        
        alert('✓ Item added successfully! Item ID: ' + itemId);
        closeModal('addItemModal');
        
        // Clear form
        document.getElementById('itemName').value = '';
        document.getElementById('itemCategory').value = 'groceries';
        document.getElementById('itemQuantity').value = '';
        document.getElementById('itemUnit').value = 'pcs';
        document.getElementById('itemCostPrice').value = '';
        document.getElementById('itemSellingPrice').value = '';
        document.getElementById('itemMinStock').value = '10';
        document.getElementById('itemExpiryDate').value = '';
        
        // Reload inventory
        await loadInventoryData();
        
    } catch (error) {
        console.error('Failed to add item:', error);
        alert('❌ Failed to add item: ' + error.message);
    }
}

// Add udhaar function with data reload
async function addUdhaarEntry() {
    const customerName = document.getElementById('udhaarCustomerName').value.trim();
    const amount = parseFloat(document.getElementById('udhaarAmount').value) || 0;
    const dueDate = document.getElementById('udhaarDueDate').value;
    const items = document.getElementById('udhaarItems').value.split(',').map(s => s.trim()).filter(s => s);
    
    if (!customerName || !amount || !dueDate) {
        alert('⚠️ Please fill all required fields (Customer Name, Amount, Due Date)');
        return;
    }
    
    // Auto-generate customer ID
    const customerId = 'CUST-' + Date.now();
    
    const entry = {
        customerId: customerId,
        customerName: customerName,
        amount: amount,
        dueDate: dueDate,
        items: items
    };
    
    try {
        console.log('Adding udhaar entry:', entry);
        const response = await apiPost('/udhaar', entry);
        console.log('Udhaar added successfully:', response);
        
        alert('✓ Udhaar added successfully! Customer ID: ' + customerId);
        closeModal('addUdhaarModal');
        
        // Clear form
        document.getElementById('udhaarCustomerName').value = '';
        document.getElementById('udhaarAmount').value = '';
        document.getElementById('udhaarDueDate').value = '';
        document.getElementById('udhaarItems').value = '';
        
        // Reload udhaar
        await loadUdhaarData();
        
    } catch (error) {
        console.error('Failed to add udhaar:', error);
        alert('❌ Failed to add udhaar: ' + error.message);
    }
}

// Edit inventory item
let editingItemId = null;

function editInventoryItem(item) {
    editingItemId = item.itemId;
    
    // Populate form with existing values
    document.getElementById('itemName').value = item.name;
    document.getElementById('itemCategory').value = item.category;
    document.getElementById('itemQuantity').value = item.quantity;
    document.getElementById('itemUnit').value = item.unit;
    document.getElementById('itemCostPrice').value = item.costPrice;
    document.getElementById('itemSellingPrice').value = item.sellingPrice;
    document.getElementById('itemMinStock').value = item.minStockLevel || 10;
    document.getElementById('itemExpiryDate').value = item.expiryDate || '';
    
    // Change modal title and button text
    document.querySelector('#addItemModal .modal-header h3').textContent = 'Edit Item';
    const submitBtn = document.querySelector('#addItemModal button[onclick="addInventoryItem()"]');
    if (submitBtn) {
        submitBtn.textContent = '💾 Update Item';
    }
    
    // Show modal
    document.getElementById('addItemModal').classList.add('active');
}

// Delete inventory item
async function deleteInventoryItem(itemId, itemName) {
    const confirmed = confirm(`Are you sure you want to delete "${itemName}"?\n\nThis action cannot be undone.`);
    
    if (!confirmed) {
        return;
    }
    
    try {
        console.log('Deleting item:', itemId);
        
        // Use POST with delete action as workaround for API Gateway auth issues
        const deleteData = {
            _action: 'delete',
            itemId: itemId
        };
        
        const response = await apiPost('/inventory', deleteData);
        console.log('Delete successful:', response);
        
        alert('✓ Item deleted successfully!');
        
        // Reload inventory
        await loadInventoryData();
        
    } catch (error) {
        console.error('Failed to delete item:', error);
        alert('❌ Failed to delete item: ' + error.message);
    }
}
