// Samaan Sathi - AI-Powered Shop Management
// Frontend Application Logic

// Configuration
const API_URL = 'http://localhost:3000'; // Local mock server for demo
let currentUser = null;
let shopData = null;
let aiResults = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

// Auth Functions
function checkAuth() {
    const user = localStorage.getItem('currentUser');
    if (user) {
        currentUser = JSON.parse(user);
        showMainApp();
        loadDashboard();
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
    document.getElementById('shopName').textContent = currentUser?.shopName || 'My Shop';
}

function showAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
        tabs[1].classList.add('active');
    }
}

async function login(event) {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    // For demo: accept any credentials
    currentUser = {
        username,
        shopName: 'Ramesh General Store',
        shopId: 'SHOP001'
    };
    
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    showMessage('Login successful!', 'success');
    
    setTimeout(() => {
        showMainApp();
        loadDashboard();
    }, 500);
}

async function register(event) {
    event.preventDefault();
    const shopName = document.getElementById('regShopName').value;
    const ownerName = document.getElementById('regOwnerName').value;
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const phone = document.getElementById('regPhone').value;
    
    // For demo: auto-register
    currentUser = {
        username,
        shopName,
        ownerName,
        phone,
        shopId: 'SHOP' + Date.now().toString().slice(-6)
    };
    
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    showMessage('Registration successful!', 'success');
    
    setTimeout(() => {
        showMainApp();
        loadDashboard();
    }, 500);
}

function logout() {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('shopData');
    currentUser = null;
    shopData = null;
    aiResults = null;
    showAuthScreen();
}

function showMessage(text, type = 'success') {
    const msg = document.getElementById('authMessage');
    msg.textContent = text;
    msg.className = `message ${type}`;
    msg.style.display = 'block';
    
    setTimeout(() => {
        msg.style.display = 'none';
    }, 3000);
}

// Navigation
function showSection(sectionName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');
    
    // Load section data
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'sales':
            loadSales();
            break;
        case 'udhaar':
            loadUdhaar();
            break;
    }
}

// Load Demo Data
async function loadDemoData() {
    if (!confirm('Load demo data? This will replace existing data.')) return;
    
    showLoading('Loading demo data...');
    
    // Simulate API call
    await sleep(1000);
    
    // Load mock data from our generator
    shopData = generateMockData();
    localStorage.setItem('shopData', JSON.stringify(shopData));
    
    showToast('✅ Demo data loaded successfully!');
    loadDashboard();
}

function generateMockData() {
    // Generate realistic mock data
    const inventory = [
        {itemId: 'ITEM001', name: 'Rice 1kg', category: 'groceries', quantity: 45, costPrice: 40, sellingPrice: 50, salesVelocity: 5.2},
        {itemId: 'ITEM002', name: 'Wheat Flour 1kg', category: 'groceries', quantity: 32, costPrice: 35, sellingPrice: 45, salesVelocity: 4.8},
        {itemId: 'ITEM003', name: 'Sugar 1kg', category: 'groceries', quantity: 28, costPrice: 38, sellingPrice: 48, salesVelocity: 3.5},
        {itemId: 'ITEM004', name: 'Salt 1kg', category: 'groceries', quantity: 15, costPrice: 18, sellingPrice: 25, salesVelocity: 2.1},
        {itemId: 'ITEM005', name: 'Cooking Oil 1L', category: 'groceries', quantity: 22, costPrice: 120, sellingPrice: 150, salesVelocity: 3.8},
        {itemId: 'ITEM006', name: 'Toor Dal 1kg', category: 'groceries', quantity: 18, costPrice: 90, sellingPrice: 110, salesVelocity: 2.5},
        {itemId: 'ITEM007', name: 'Tea Powder 250g', category: 'groceries', quantity: 35, costPrice: 80, sellingPrice: 100, salesVelocity: 4.2},
        {itemId: 'ITEM008', name: 'Coca Cola 600ml', category: 'beverages', quantity: 48, costPrice: 30, sellingPrice: 40, salesVelocity: 8.5},
        {itemId: 'ITEM009', name: 'Parle-G Biscuits', category: 'snacks', quantity: 60, costPrice: 8, sellingPrice: 10, salesVelocity: 12.3},
        {itemId: 'ITEM010', name: 'Maggi Noodles', category: 'snacks', quantity: 42, costPrice: 10, sellingPrice: 14, salesVelocity: 7.8}
    ];
    
    const customers = [
        {customerId: 'CUST001', customerName: 'Ramesh Kumar', phone: '+91-9876543210'},
        {customerId: 'CUST002', customerName: 'Suresh Sharma', phone: '+91-9876543211'},
        {customerId: 'CUST003', customerName: 'Priya Singh', phone: '+91-9876543212'},
        {customerId: 'CUST004', customerName: 'Anjali Verma', phone: '+91-9876543213'},
        {customerId: 'CUST005', customerName: 'Vijay Kumar', phone: '+91-9876543214'}
    ];
    
    const salesHistory = generateSalesHistory(inventory, customers, 90);
    const udhaarRecords = generateUdhaarRecords(customers, salesHistory);
    
    return {
        shopId: currentUser.shopId,
        shopName: currentUser.shopName,
        cashAvailable: 15000,
        inventory,
        customers,
        salesHistory,
        udhaarRecords
    };
}

function generateSalesHistory(inventory, customers, days) {
    const sales = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    for (let i = 0; i < days * 10; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + Math.floor(i / 10));
        
        const customer = Math.random() < 0.8 ? customers[Math.floor(Math.random() * customers.length)] : null;
        const numItems = Math.floor(Math.random() * 3) + 1;
        const items = [];
        let totalAmount = 0;
        
        for (let j = 0; j < numItems; j++) {
            const item = inventory[Math.floor(Math.random() * inventory.length)];
            const quantity = Math.floor(Math.random() * 3) + 1;
            const subtotal = item.sellingPrice * quantity;
            
            items.push({
                itemId: item.itemId,
                name: item.name,
                quantity,
                price: item.sellingPrice,
                subtotal
            });
            
            totalAmount += subtotal;
        }
        
        sales.push({
            saleId: 'SALE' + (i + 1).toString().padStart(4, '0'),
            customerId: customer?.customerId,
            customerName: customer?.customerName || 'Walk-in',
            items,
            totalAmount,
            paymentMethod: Math.random() < 0.7 ? 'CASH' : 'UDHAAR',
            timestamp: date.toISOString(),
            createdAt: date.toISOString()
        });
    }
    
    return sales;
}

function generateUdhaarRecords(customers, salesHistory) {
    const udhaarSales = salesHistory.filter(s => s.paymentMethod === 'UDHAAR' && s.customerId);
    
    return udhaarSales.map((sale, i) => {
        const isPaid = Math.random() < 0.6;
        const createdDate = new Date(sale.timestamp);
        const paidDate = isPaid ? new Date(createdDate.getTime() + Math.random() * 30 * 24 * 60 * 60 * 1000) : null;
        
        return {
            udhaarId: 'UDHAAR' + (i + 1).toString().padStart(4, '0'),
            customerId: sale.customerId,
            customerName: sale.customerName,
            saleId: sale.saleId,
            amount: sale.totalAmount,
            paidAmount: isPaid ? sale.totalAmount : 0,
            remainingAmount: isPaid ? 0 : sale.totalAmount,
            status: isPaid ? 'PAID' : (Math.random() < 0.7 ? 'PENDING' : 'OVERDUE'),
            createdAt: createdDate.toISOString(),
            paidAt: paidDate?.toISOString(),
            dueDate: new Date(createdDate.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString()
        };
    });
}

// Dashboard
function loadDashboard() {
    const data = getShopData();
    if (!data) {
        document.getElementById('cashAvailable').textContent = '₹0';
        document.getElementById('outstandingUdhaar').textContent = '₹0';
        document.getElementById('inventoryCount').textContent = '0';
        document.getElementById('customerCount').textContent = '0';
        return;
    }
    
    // Update metrics
    document.getElementById('cashAvailable').textContent = `₹${data.cashAvailable.toLocaleString()}`;
    
    const outstanding = data.udhaarRecords
        .filter(u => u.status !== 'PAID')
        .reduce((sum, u) => sum + u.remainingAmount, 0);
    document.getElementById('outstandingUdhaar').textContent = `₹${outstanding.toLocaleString()}`;
    
    document.getElementById('inventoryCount').textContent = data.inventory.length;
    document.getElementById('customerCount').textContent = data.customers.length;
    
    // Show AI results if available
    if (aiResults) {
        displayAIResults(aiResults);
    }
}

function displayAIResults(results) {
    // Display AI status
    const statusHtml = `
        <div style="padding: 1rem; background: #d1fae5; border-radius: 0.5rem; color: #065f46;">
            <strong>✅ AI Analysis Complete</strong>
            <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                Processed ${results.summary?.itemsTracked || 0} items, 
                ${results.summary?.customersTracked || 0} customers. 
                Generated ${results.summary?.totalAlerts || 0} alerts.
            </p>
        </div>
    `;
    document.getElementById('aiStatus').innerHTML = statusHtml;
    
    // Display alerts
    const alertsHtml = results.alerts && results.alerts.length > 0
        ? results.alerts.map(alert => `
            <div class="alert ${alert.severity.toLowerCase()}">
                <span>${alert.message}</span>
            </div>
        `).join('')
        : '<p class="empty-state">No critical alerts</p>';
    document.getElementById('aiAlerts').innerHTML = alertsHtml;
    
    // Display insights
    const insightsHtml = results.insights && results.insights.length > 0
        ? results.insights.map(insight => `
            <div class="insight">
                <strong>${insight.type}:</strong> ${insight.message}
            </div>
        `).join('')
        : '<p class="empty-state">No insights available</p>';
    document.getElementById('aiInsights').innerHTML = insightsHtml;
}

// Run AI Batch Analysis
async function runAIBatch() {
    const data = getShopData();
    if (!data) {
        alert('⚠️ Please load demo data first');
        return;
    }
    
    showLoading('Running AI analysis...');
    
    // Simulate AI processing
    await sleep(2000);
    
    // Run all AI engines locally (mock)
    aiResults = runLocalAIEngines(data);
    localStorage.setItem('aiResults', JSON.stringify(aiResults));
    
    showToast('✅ AI analysis complete!');
    loadDashboard();
}

function runLocalAIEngines(data) {
    // Mock AI results based on our engine logic
    const results = {
        shopId: data.shopId,
        processedAt: new Date().toISOString(),
        forecasts: {},
        creditScores: {},
        reorderPlan: {},
        cashFlowSimulation: {},
        pricingRecommendations: {},
        insights: [],
        alerts: [],
        summary: {}
    };
    
    // Generate forecasts
    data.inventory.forEach(item => {
        const forecast = generateMockForecast(item, data.salesHistory);
        results.forecasts[item.itemId] = forecast;
        
        // Check for stockout risk
        if (item.quantity < forecast.totalForecast * 0.3) {
            results.alerts.push({
                type: 'STOCKOUT_RISK',
                severity: 'HIGH',
                message: `⚠️ ${item.name} critically low. Need ${Math.ceil(forecast.totalForecast - item.quantity)} units.`,
                itemId: item.itemId
            });
        }
    });
    
    // Generate credit scores
    data.customers.forEach(customer => {
        const score = generateMockCreditScore(customer, data.udhaarRecords);
        results.creditScores[customer.customerId] = score;
        
        if (score.riskCategory === 'HIGH_RISK' && score.currentOutstanding > 0) {
            results.alerts.push({
                type: 'HIGH_RISK_CUSTOMER',
                severity: 'MEDIUM',
                message: `⚠️ ${customer.customerName} is high-risk. Outstanding: ₹${score.currentOutstanding.toFixed(0)}`,
                customerId: customer.customerId
            });
        }
    });
    
    // Cash flow simulation
    const udhaarOutstanding = data.udhaarRecords
        .filter(u => u.status !== 'PAID')
        .reduce((sum, u) => sum + u.remainingAmount, 0);
    
    results.cashFlowSimulation = generateMockCashFlowSimulation(
        data.cashAvailable,
        udhaarOutstanding
    );
    
    if (results.cashFlowSimulation.survivalMode.activated) {
        results.alerts.push({
            type: 'SURVIVAL_MODE',
            severity: 'CRITICAL',
            message: `🚨 SURVIVAL MODE: ${results.cashFlowSimulation.analysis.riskLevel} risk detected`,
            triggers: results.cashFlowSimulation.survivalMode.triggers
        });
    }
    
    // Reorder optimization
    results.reorderPlan = generateMockReorderPlan(
        data.inventory,
        results.forecasts,
        data.cashAvailable,
        udhaarOutstanding
    );
    
    // Pricing recommendations
    data.inventory.slice(0, 5).forEach(item => {
        results.pricingRecommendations[item.itemId] = generateMockPricingRecommendation(item);
    });
    
    // Summary
    results.summary = {
        itemsTracked: data.inventory.length,
        customersTracked: data.customers.length,
        totalAlerts: results.alerts.length,
        cashFlowStatus: results.cashFlowSimulation.analysis.riskLevel
    };
    
    return results;
}

// Mock AI Engine Functions
function generateMockForecast(item, salesHistory) {
    const baseDaily = item.salesVelocity || 5;
    const days = 7;
    const forecast = [];
    
    for (let i = 1; i <= days; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        let predicted = baseDaily * (isWeekend ? 1.3 : 1);
        predicted += (Math.random() - 0.5) * baseDaily * 0.3; // Add noise
        predicted = Math.max(0, Math.round(predicted));
        
        forecast.push({
            date: date.toISOString().split('T')[0],
            predictedQuantity: predicted,
            dayOfWeek: date.toLocaleDateString('en-US', {weekday: 'short'}),
            isWeekend,
            isFestival: false,
            confidence: 0.75 + Math.random() * 0.15
        });
    }
    
    const totalForecast = forecast.reduce((sum, f) => sum + f.predictedQuantity, 0);
    const shortage = Math.max(0, totalForecast - item.quantity);
    
    return {
        itemId: item.itemId,
        itemName: item.name,
        currentStock: item.quantity,
        totalForecast,
        forecast,
        recommendation: shortage > 0 
            ? `⚠️ Stock ${item.name} soon. Need ${shortage} more units.`
            : `✓ ${item.name} stock adequate for next ${days} days.`,
        confidence: 0.82,
        mape: 12.5,
        trend: 'stable'
    };
}

function generateMockCreditScore(customer, udhaarRecords) {
    const customerUdhaar = udhaarRecords.filter(u => u.customerId === customer.customerId);
    const paidCount = customerUdhaar.filter(u => u.status === 'PAID').length;
    const totalCount = customerUdhaar.length || 1;
    const paymentRate = paidCount / totalCount;
    
    const riskScore = Math.min(100, paymentRate * 100 + Math.random() * 20);
    
    let riskCategory, creditLimit;
    if (riskScore >= 80) {
        riskCategory = 'RELIABLE_PAYER';
        creditLimit = 8000;
    } else if (riskScore >= 60) {
        riskCategory = 'SEASONAL_BORROWER';
        creditLimit = 6000;
    } else if (riskScore >= 40) {
        riskCategory = 'MODERATE_RISK';
        creditLimit = 4000;
    } else {
        riskCategory = 'HIGH_RISK';
        creditLimit = 2000;
    }
    
    const currentOutstanding = customerUdhaar
        .filter(u => u.status !== 'PAID')
        .reduce((sum, u) => sum + u.remainingAmount, 0);
    
    return {
        customerId: customer.customerId,
        customerName: customer.customerName,
        riskScore: Math.round(riskScore),
        riskCategory,
        recommendedCreditLimit: creditLimit,
        currentOutstanding,
        creditUtilization: (currentOutstanding / creditLimit * 100).toFixed(1),
        insights: riskCategory === 'RELIABLE_PAYER' 
            ? [`✓ ${customer.customerName} is reliable. Safe for higher credit.`]
            : [`⚠️ Monitor ${customer.customerName} closely.`]
    };
}

function generateMockCashFlowSimulation(cashAvailable, udhaarOutstanding) {
    const udhaarRatio = cashAvailable > 0 ? udhaarOutstanding / cashAvailable : 999;
    
    let riskLevel, cashCrunchProbability;
    if (udhaarRatio > 2 || cashAvailable < 5000) {
        riskLevel = 'CRITICAL';
        cashCrunchProbability = 65;
    } else if (udhaarRatio > 1 || cashAvailable < 10000) {
        riskLevel = 'HIGH';
        cashCrunchProbability = 35;
    } else if (udhaarRatio > 0.5) {
        riskLevel = 'MEDIUM';
        cashCrunchProbability = 15;
    } else {
        riskLevel = 'LOW';
        cashCrunchProbability = 5;
    }
    
    const survivalMode = {
        activated: riskLevel === 'CRITICAL' || riskLevel === 'HIGH',
        triggers: riskLevel === 'CRITICAL' 
            ? ['Critical cash level', `${cashCrunchProbability}% chance of cash crunch`]
            : riskLevel === 'HIGH'
            ? ['High cash flow risk detected']
            : [],
        actions: riskLevel === 'CRITICAL' || riskLevel === 'HIGH'
            ? ['Reduce udhaar limits by 30%', 'Prioritize high-margin items', 'Accelerate collections']
            : [],
        severity: riskLevel
    };
    
    return {
        currentCash: cashAvailable,
        udhaarOutstanding,
        analysis: {
            riskLevel,
            cashCrunchProbability,
            projections: {
                pessimistic: { finalCash: cashAvailable * 0.6 },
                expected: { finalCash: cashAvailable * 0.85 },
                optimistic: { finalCash: cashAvailable * 1.1 }
            }
        },
        survivalMode
    };
}

function generateMockReorderPlan(inventory, forecasts, cashAvailable, udhaarOutstanding) {
    const udhaarRatio = cashAvailable > 0 ? udhaarOutstanding / cashAvailable : 999;
    
    let mode, status;
    if (udhaarRatio > 2 || cashAvailable < 5000) {
        mode = 'SURVIVAL';
        status = 'CRITICAL';
    } else if (udhaarRatio > 1) {
        mode = 'CONSERVATIVE';
        status = 'WARNING';
    } else {
        mode = 'BALANCED';
        status = 'HEALTHY';
    }
    
    const reorderPlan = [];
    let remainingCash = cashAvailable * 0.7; // Reserve 30%
    
    inventory.forEach(item => {
        const forecast = forecasts[item.itemId];
        if (!forecast) return;
        
        const shortage = Math.max(0, forecast.totalForecast - item.quantity);
        if (shortage === 0) return;
        
        const cost = shortage * item.costPrice;
        if (cost > remainingCash) return;
        
        const margin = ((item.sellingPrice - item.costPrice) / item.sellingPrice * 100).toFixed(1);
        
        reorderPlan.push({
            itemId: item.itemId,
            name: item.name,
            recommendedQty: shortage,
            totalCost: cost,
            marginPct: parseFloat(margin),
            reason: mode === 'SURVIVAL' 
                ? `High-margin (${margin}%), essential`
                : `Predicted shortage: ${shortage} units`,
            status: 'RECOMMENDED'
        });
        
        remainingCash -= cost;
    });
    
    const totalInvestment = reorderPlan.reduce((sum, p) => sum + p.totalCost, 0);
    const expectedProfit = reorderPlan.reduce((sum, p) => {
        const item = inventory.find(i => i.itemId === p.itemId);
        return sum + (item.sellingPrice - item.costPrice) * p.recommendedQty;
    }, 0);
    
    return {
        cashFlowHealth: { status, mode },
        reorderPlan,
        impact: {
            totalInvestment,
            expectedProfit,
            expectedROI: totalInvestment > 0 ? (expectedProfit / totalInvestment * 100).toFixed(1) : 0
        }
    };
}

function generateMockPricingRecommendation(item) {
    const elasticity = -1.2 + Math.random() * 0.8;
    const currentMargin = ((item.sellingPrice - item.costPrice) / item.sellingPrice * 100);
    
    let optimalPrice = item.sellingPrice;
    let recommendation = `✓ ${item.name} is optimally priced.`;
    
    if (currentMargin < 20) {
        optimalPrice = item.sellingPrice * 1.05;
        recommendation = `Increase ${item.name} by ₹${(optimalPrice - item.sellingPrice).toFixed(2)}. Low margin detected.`;
    } else if (currentMargin > 35) {
        optimalPrice = item.sellingPrice * 0.97;
        recommendation = `Decrease ${item.name} by ₹${(item.sellingPrice - optimalPrice).toFixed(2)}. Boost volume.`;
    }
    
    return {
        itemId: item.itemId,
        itemName: item.name,
        currentPrice: item.sellingPrice,
        optimalPrice: Math.round(optimalPrice),
        priceChange: Math.round(optimalPrice - item.sellingPrice),
        elasticity: elasticity.toFixed(2),
        recommendation,
        confidence: 0.78
    };
}

// Inventory Section
function loadInventory() {
    const data = getShopData();
    if (!data || !data.inventory) {
        document.getElementById('inventoryList').innerHTML = '<p class="empty-state">No inventory items.</p>';
        return;
    }
    
    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Item Name</th>
                    <th>Category</th>
                    <th>Quantity</th>
                    <th>Cost Price</th>
                    <th>Selling Price</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>
                ${data.inventory.map(item => {
                    const margin = ((item.sellingPrice - item.costPrice) / item.sellingPrice * 100).toFixed(1);
                    return `
                        <tr>
                            <td><strong>${item.name}</strong></td>
                            <td><span class="badge">${item.category}</span></td>
                            <td>${item.quantity}</td>
                            <td>₹${item.costPrice}</td>
                            <td>₹${item.sellingPrice}</td>
                            <td>${margin}%</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('inventoryList').innerHTML = html;
}

function showReorderPlan() {
    if (!aiResults || !aiResults.reorderPlan) {
        alert('⚠️ Please run AI analysis first');
        return;
    }
    
    const plan = aiResults.reorderPlan;
    const html = `
        <div class="card">
            <h3>🤖 AI Reorder Plan</h3>
            <div style="padding: 1rem; background: var(--bg); border-radius: 0.5rem; margin-bottom: 1rem;">
                <strong>Cash Flow Status:</strong> ${plan.cashFlowHealth.status} (${plan.cashFlowHealth.mode} mode)<br>
                <strong>Total Investment:</strong> ₹${plan.impact.totalInvestment.toFixed(0)}<br>
                <strong>Expected Profit:</strong> ₹${plan.impact.expectedProfit.toFixed(0)}<br>
                <strong>Expected ROI:</strong> ${plan.impact.expectedROI}%
            </div>
            <table class="table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Cost</th>
                        <th>Margin</th>
                        <th>Reason</th>
                    </tr>
                </thead>
                <tbody>
                    ${plan.reorderPlan.map(item => `
                        <tr>
                            <td><strong>${item.name}</strong></td>
                            <td>${item.recommendedQty}</td>
                            <td>₹${item.totalCost.toFixed(0)}</td>
                            <td>${item.marginPct}%</td>
                            <td style="font-size: 0.875rem;">${item.reason}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('inventoryList').innerHTML = html;
}

// Sales Section
function loadSales() {
    const data = getShopData();
    if (!data || !data.salesHistory) {
        document.getElementById('salesList').innerHTML = '<p class="empty-state">No sales recorded.</p>';
        return;
    }
    
    const recentSales = data.salesHistory.slice(-20).reverse();
    
    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Items</th>
                    <th>Amount</th>
                    <th>Payment</th>
                </tr>
            </thead>
            <tbody>
                ${recentSales.map(sale => `
                    <tr>
                        <td>${new Date(sale.timestamp).toLocaleDateString()}</td>
                        <td>${sale.customerName}</td>
                        <td>${sale.items.length} items</td>
                        <td>₹${sale.totalAmount.toFixed(2)}</td>
                        <td><span class="badge ${sale.paymentMethod === 'CASH' ? 'success' : 'warning'}">${sale.paymentMethod}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('salesList').innerHTML = html;
}

// Udhaar Section
function loadUdhaar() {
    const data = getShopData();
    if (!data || !data.udhaarRecords) {
        document.getElementById('udhaarList').innerHTML = '<p class="empty-state">No udhaar records.</p>';
        return;
    }
    
    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Paid</th>
                    <th>Remaining</th>
                    <th>Status</th>
                    <th>Due Date</th>
                </tr>
            </thead>
            <tbody>
                ${data.udhaarRecords.map(record => `
                    <tr>
                        <td><strong>${record.customerName}</strong></td>
                        <td>₹${record.amount.toFixed(2)}</td>
                        <td>₹${record.paidAmount.toFixed(2)}</td>
                        <td>₹${record.remainingAmount.toFixed(2)}</td>
                        <td><span class="badge ${
                            record.status === 'PAID' ? 'success' : 
                            record.status === 'OVERDUE' ? 'danger' : 'warning'
                        }">${record.status}</span></td>
                        <td>${new Date(record.dueDate).toLocaleDateString()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('udhaarList').innerHTML = html;
}

function showCreditScores() {
    if (!aiResults || !aiResults.creditScores) {
        alert('⚠️ Please run AI analysis first');
        return;
    }
    
    const scores = Object.values(aiResults.creditScores);
    
    const html = `
        <div class="card">
            <h3>🤖 Credit Risk Scores</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Customer</th>
                        <th>Risk Score</th>
                        <th>Category</th>
                        <th>Credit Limit</th>
                        <th>Outstanding</th>
                        <th>Utilization</th>
                    </tr>
                </thead>
                <tbody>
                    ${scores.map(score => `
                        <tr>
                            <td><strong>${score.customerName}</strong></td>
                            <td>${score.riskScore}/100</td>
                            <td><span class="badge ${
                                score.riskCategory === 'RELIABLE_PAYER' ? 'success' :
                                score.riskCategory === 'HIGH_RISK' ? 'danger' : 'warning'
                            }">${score.riskCategory.replace(/_/g, ' ')}</span></td>
                            <td>₹${score.recommendedCreditLimit}</td>
                            <td>₹${score.currentOutstanding.toFixed(0)}</td>
                            <td>${score.creditUtilization}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('udhaarList').innerHTML = html;
}

// Forecast Section
function generateForecasts() {
    if (!aiResults || !aiResults.forecasts) {
        alert('⚠️ Please run AI analysis first');
        return;
    }
    
    const forecasts = Object.values(aiResults.forecasts).slice(0, 5);
    const days = parseInt(document.getElementById('forecastDays').value) || 7;
    
    const html = forecasts.map(forecast => `
        <div class="card">
            <h4>${forecast.itemName}</h4>
            <p style="color: var(--text-light); margin-bottom: 1rem;">
                Current Stock: ${forecast.currentStock} | 
                ${days}-Day Forecast: ${forecast.totalForecast} units | 
                Confidence: ${(forecast.confidence * 100).toFixed(0)}%
            </p>
            <div class="forecast-chart">
                ${forecast.forecast.slice(0, days).map(day => `
                    <div class="forecast-day">
                        <div class="date">${new Date(day.date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}</div>
                        <div class="quantity">${day.predictedQuantity}</div>
                        ${day.isWeekend ? '<div style="font-size: 0.75rem;">📅 Weekend</div>' : ''}
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: var(--bg); border-radius: 0.5rem;">
                ${forecast.recommendation}
            </div>
        </div>
    `).join('');
    
    document.getElementById('forecastList').innerHTML = html;
}

// Pricing Section
function generatePricingRecommendations() {
    if (!aiResults || !aiResults.pricingRecommendations) {
        alert('⚠️ Please run AI analysis first');
        return;
    }
    
    const recommendations = Object.values(aiResults.pricingRecommendations);
    
    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Current Price</th>
                    <th>Optimal Price</th>
                    <th>Change</th>
                    <th>Elasticity</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
                ${recommendations.map(rec => `
                    <tr>
                        <td><strong>${rec.itemName}</strong></td>
                        <td>₹${rec.currentPrice}</td>
                        <td>₹${rec.optimalPrice}</td>
                        <td style="color: ${rec.priceChange > 0 ? 'var(--success)' : rec.priceChange < 0 ? 'var(--danger)' : 'var(--text-light)'}">
                            ${rec.priceChange > 0 ? '+' : ''}₹${rec.priceChange}
                        </td>
                        <td>${rec.elasticity}</td>
                        <td style="font-size: 0.875rem;">${rec.recommendation}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('pricingList').innerHTML = html;
}

// Utility Functions
function getShopData() {
    if (shopData) return shopData;
    
    const stored = localStorage.getItem('shopData');
    if (stored) {
        shopData = JSON.parse(stored);
        return shopData;
    }
    
    return null;
}

function showLoading(message = 'Loading...') {
    // Simple loading indicator
    console.log('Loading:', message);
}

function showToast(message) {
    // Simple toast notification
    alert(message);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize on load
console.log('Samaan Sathi AI - Frontend Loaded');
