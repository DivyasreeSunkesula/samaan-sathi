"""
Samaan Sathi - AI-Powered Shop Management
Streamlit Application
"""
import streamlit as st
import json
import random
from datetime import datetime, timedelta
import pandas as pd

# Page config
st.set_page_config(
    page_title="Samaan Sathi - AI Shop Management",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .alert-critical {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-high {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .insight-card {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'shop_data' not in st.session_state:
    st.session_state.shop_data = None
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Generate mock data function
def generate_mock_data():
    inventory = [
        {'itemId': 'ITEM001', 'name': 'Rice 1kg', 'category': 'groceries', 'quantity': 45, 'costPrice': 40, 'sellingPrice': 50, 'salesVelocity': 5.2},
        {'itemId': 'ITEM002', 'name': 'Wheat Flour 1kg', 'category': 'groceries', 'quantity': 32, 'costPrice': 35, 'sellingPrice': 45, 'salesVelocity': 4.8},
        {'itemId': 'ITEM003', 'name': 'Sugar 1kg', 'category': 'groceries', 'quantity': 28, 'costPrice': 38, 'sellingPrice': 48, 'salesVelocity': 3.5},
        {'itemId': 'ITEM004', 'name': 'Salt 1kg', 'category': 'groceries', 'quantity': 15, 'costPrice': 18, 'sellingPrice': 25, 'salesVelocity': 2.1},
        {'itemId': 'ITEM005', 'name': 'Cooking Oil 1L', 'category': 'groceries', 'quantity': 22, 'costPrice': 120, 'sellingPrice': 150, 'salesVelocity': 3.8},
        {'itemId': 'ITEM006', 'name': 'Toor Dal 1kg', 'category': 'groceries', 'quantity': 18, 'costPrice': 90, 'sellingPrice': 110, 'salesVelocity': 2.5},
        {'itemId': 'ITEM007', 'name': 'Tea Powder 250g', 'category': 'groceries', 'quantity': 35, 'costPrice': 80, 'sellingPrice': 100, 'salesVelocity': 4.2},
        {'itemId': 'ITEM008', 'name': 'Coca Cola 600ml', 'category': 'beverages', 'quantity': 48, 'costPrice': 30, 'sellingPrice': 40, 'salesVelocity': 8.5},
        {'itemId': 'ITEM009', 'name': 'Parle-G Biscuits', 'category': 'snacks', 'quantity': 60, 'costPrice': 8, 'sellingPrice': 10, 'salesVelocity': 12.3},
        {'itemId': 'ITEM010', 'name': 'Maggi Noodles', 'category': 'snacks', 'quantity': 42, 'costPrice': 10, 'sellingPrice': 14, 'salesVelocity': 7.8}
    ]
    
    customers = [
        {'customerId': 'CUST001', 'customerName': 'Ramesh Kumar', 'phone': '+91-9876543210'},
        {'customerId': 'CUST002', 'customerName': 'Suresh Sharma', 'phone': '+91-9876543211'},
        {'customerId': 'CUST003', 'customerName': 'Priya Singh', 'phone': '+91-9876543212'},
        {'customerId': 'CUST004', 'customerName': 'Anjali Verma', 'phone': '+91-9876543213'},
        {'customerId': 'CUST005', 'customerName': 'Vijay Kumar', 'phone': '+91-9876543214'}
    ]
    
    # Generate sales and udhaar
    sales_history = []
    udhaar_records = []
    
    for i in range(200):
        customer = random.choice(customers)
        items = random.sample(inventory, random.randint(1, 3))
        total = sum(item['sellingPrice'] * random.randint(1, 3) for item in items)
        payment_method = random.choice(['CASH', 'CASH', 'CASH', 'UDHAAR'])
        
        sale = {
            'saleId': f'SALE{i+1:04d}',
            'customerId': customer['customerId'],
            'customerName': customer['customerName'],
            'totalAmount': total,
            'paymentMethod': payment_method,
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat()
        }
        sales_history.append(sale)
        
        if payment_method == 'UDHAAR':
            status = random.choice(['PAID', 'PAID', 'PENDING', 'OVERDUE'])
            udhaar_records.append({
                'udhaarId': f'UDHAAR{len(udhaar_records)+1:04d}',
                'customerId': customer['customerId'],
                'customerName': customer['customerName'],
                'amount': total,
                'paidAmount': total if status == 'PAID' else 0,
                'remainingAmount': 0 if status == 'PAID' else total,
                'status': status
            })
    
    return {
        'shopId': 'SHOP001',
        'shopName': 'Ramesh General Store',
        'cashAvailable': 15000,
        'inventory': inventory,
        'customers': customers,
        'salesHistory': sales_history,
        'udhaarRecords': udhaar_records
    }

# Run AI analysis
def run_ai_analysis(data):
    results = {
        'forecasts': {},
        'creditScores': {},
        'reorderPlan': {},
        'cashFlowSimulation': {},
        'pricingRecommendations': {},
        'alerts': [],
        'insights': []
    }
    
    # Generate forecasts
    for item in data['inventory'][:5]:
        forecast_days = []
        for i in range(7):
            date = datetime.now() + timedelta(days=i+1)
            qty = int(item['salesVelocity'] * (1.3 if date.weekday() in [5,6] else 1) * random.uniform(0.8, 1.2))
            forecast_days.append({
                'date': date.strftime('%Y-%m-%d'),
                'predictedQuantity': qty,
                'confidence': 0.75 + random.random() * 0.15
            })
        
        total_forecast = sum(f['predictedQuantity'] for f in forecast_days)
        shortage = max(0, total_forecast - item['quantity'])
        
        results['forecasts'][item['itemId']] = {
            'itemName': item['name'],
            'currentStock': item['quantity'],
            'totalForecast': total_forecast,
            'forecast': forecast_days,
            'recommendation': f"⚠️ Need {shortage} units" if shortage > 0 else "✓ Stock adequate"
        }
        
        if shortage > item['quantity'] * 0.5:
            results['alerts'].append({
                'severity': 'HIGH',
                'message': f"⚠️ {item['name']} critically low. Need {shortage} units."
            })
    
    # Credit scores
    for customer in data['customers']:
        customer_udhaar = [u for u in data['udhaarRecords'] if u['customerId'] == customer['customerId']]
        paid_count = len([u for u in customer_udhaar if u['status'] == 'PAID'])
        total_count = len(customer_udhaar) or 1
        
        risk_score = int((paid_count / total_count) * 100)
        
        if risk_score >= 80:
            category = 'RELIABLE_PAYER'
            limit = 8000
        elif risk_score >= 60:
            category = 'SEASONAL_BORROWER'
            limit = 6000
        else:
            category = 'HIGH_RISK'
            limit = 2000
        
        outstanding = sum(u['remainingAmount'] for u in customer_udhaar if u['status'] != 'PAID')
        
        results['creditScores'][customer['customerId']] = {
            'customerName': customer['customerName'],
            'riskScore': risk_score,
            'riskCategory': category,
            'recommendedCreditLimit': limit,
            'currentOutstanding': outstanding
        }
        
        if category == 'HIGH_RISK' and outstanding > 0:
            results['alerts'].append({
                'severity': 'MEDIUM',
                'message': f"⚠️ {customer['customerName']} is high-risk. Outstanding: ₹{outstanding:.0f}"
            })
    
    # Cash flow
    udhaar_outstanding = sum(u['remainingAmount'] for u in data['udhaarRecords'] if u['status'] != 'PAID')
    cash_ratio = udhaar_outstanding / data['cashAvailable'] if data['cashAvailable'] > 0 else 999
    
    if cash_ratio > 1.5:
        risk_level = 'CRITICAL'
        results['alerts'].append({
            'severity': 'CRITICAL',
            'message': '🚨 SURVIVAL MODE: Critical cash flow risk'
        })
    elif cash_ratio > 0.8:
        risk_level = 'HIGH'
    else:
        risk_level = 'LOW'
    
    results['cashFlowSimulation'] = {
        'riskLevel': risk_level,
        'cashCrunchProbability': int(cash_ratio * 30),
        'currentCash': data['cashAvailable'],
        'udhaarOutstanding': udhaar_outstanding
    }
    
    # Reorder plan
    reorder_items = []
    for item in data['inventory'][:5]:
        forecast = results['forecasts'].get(item['itemId'], {})
        shortage = max(0, forecast.get('totalForecast', 0) - item['quantity'])
        if shortage > 0:
            margin = ((item['sellingPrice'] - item['costPrice']) / item['sellingPrice'] * 100)
            reorder_items.append({
                'name': item['name'],
                'recommendedQty': shortage,
                'totalCost': shortage * item['costPrice'],
                'marginPct': margin,
                'reason': f"Predicted shortage: {shortage} units"
            })
    
    results['reorderPlan'] = {
        'items': reorder_items,
        'totalInvestment': sum(i['totalCost'] for i in reorder_items),
        'mode': 'CONSERVATIVE' if risk_level == 'HIGH' else 'BALANCED'
    }
    
    # Pricing
    for item in data['inventory'][:3]:
        current_margin = ((item['sellingPrice'] - item['costPrice']) / item['sellingPrice'] * 100)
        optimal_price = item['sellingPrice'] * (1.05 if current_margin < 20 else 0.98)
        
        results['pricingRecommendations'][item['itemId']] = {
            'itemName': item['name'],
            'currentPrice': item['sellingPrice'],
            'optimalPrice': int(optimal_price),
            'priceChange': int(optimal_price - item['sellingPrice']),
            'recommendation': f"{'Increase' if optimal_price > item['sellingPrice'] else 'Decrease'} by ₹{abs(int(optimal_price - item['sellingPrice']))}"
        }
    
    # Insights
    results['insights'].append({
        'type': 'CASH_FLOW',
        'message': f"Cash flow status: {risk_level}. Monitor udhaar collections closely."
    })
    
    if len(reorder_items) > 0:
        results['insights'].append({
            'type': 'REORDER',
            'message': f"Reorder {len(reorder_items)} items. Total investment: ₹{results['reorderPlan']['totalInvestment']:.0f}"
        })
    
    return results

# Login/Register Page
def show_auth_page():
    st.markdown('<div class="main-header">🏪 Samaan Sathi</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b; margin-bottom: 2rem;">AI-Powered Shop Management</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    'username': username,
                    'shopName': 'Ramesh General Store'
                }
                st.rerun()
            else:
                st.error("Please enter username and password")
    
    with tab2:
        st.subheader("Register")
        shop_name = st.text_input("Shop Name", key="reg_shop")
        owner_name = st.text_input("Owner Name", key="reg_owner")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        phone = st.text_input("Phone Number", key="reg_phone")
        
        if st.button("Register", type="primary", use_container_width=True):
            if all([shop_name, owner_name, reg_username, reg_password, phone]):
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    'username': reg_username,
                    'shopName': shop_name,
                    'ownerName': owner_name,
                    'phone': phone
                }
                st.success("✅ Registration successful!")
                st.rerun()
            else:
                st.error("Please fill all fields")

# Main App
def show_main_app():
    # Sidebar
    with st.sidebar:
        st.title("🏪 Samaan Sathi")
        st.write(f"**{st.session_state.current_user['shopName']}**")
        st.divider()
        
        if st.button("📦 Load Demo Data", use_container_width=True):
            st.session_state.shop_data = generate_mock_data()
            st.success("✅ Demo data loaded!")
            st.rerun()
        
        if st.button("🤖 Run AI Analysis", use_container_width=True, type="primary"):
            if st.session_state.shop_data:
                with st.spinner("Running AI analysis..."):
                    st.session_state.ai_results = run_ai_analysis(st.session_state.shop_data)
                st.success("✅ AI analysis complete!")
                st.rerun()
            else:
                st.error("Please load demo data first")
        
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📦 Inventory", "💰 Sales", "📝 Udhaar", "📈 Forecast", "💵 Pricing"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.shop_data = None
            st.session_state.ai_results = None
            st.rerun()
    
    # Main content
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📦 Inventory":
        show_inventory()
    elif page == "💰 Sales":
        show_sales()
    elif page == "📝 Udhaar":
        show_udhaar()
    elif page == "📈 Forecast":
        show_forecast()
    elif page == "💵 Pricing":
        show_pricing()

def show_dashboard():
    st.title("📊 AI Dashboard")
    
    if not st.session_state.shop_data:
        st.info("👈 Click 'Load Demo Data' in the sidebar to get started")
        return
    
    data = st.session_state.shop_data
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cash Available", f"₹{data['cashAvailable']:,}")
    
    with col2:
        outstanding = sum(u['remainingAmount'] for u in data['udhaarRecords'] if u['status'] != 'PAID')
        st.metric("Outstanding Udhaar", f"₹{outstanding:,}")
    
    with col3:
        st.metric("Inventory Items", len(data['inventory']))
    
    with col4:
        st.metric("Total Customers", len(data['customers']))
    
    st.divider()
    
    # AI Results
    if st.session_state.ai_results:
        results = st.session_state.ai_results
        
        # AI Status
        st.success("✅ AI Analysis Complete")
        
        # Alerts
        if results['alerts']:
            st.subheader("⚠️ Critical Alerts")
            for alert in results['alerts']:
                if alert['severity'] == 'CRITICAL':
                    st.markdown(f'<div class="alert-critical">{alert["message"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-high">{alert["message"]}</div>', unsafe_allow_html=True)
        
        # Insights
        if results['insights']:
            st.subheader("🎯 AI Insights")
            for insight in results['insights']:
                st.markdown(f'<div class="insight-card"><strong>{insight["type"]}:</strong> {insight["message"]}</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Click 'Run AI Analysis' to generate insights")

def show_inventory():
    st.title("📦 Inventory Management")
    
    if not st.session_state.shop_data:
        st.info("👈 Load demo data first")
        return
    
    data = st.session_state.shop_data
    
    # Show reorder plan if AI results available
    if st.session_state.ai_results and st.button("🤖 Show AI Reorder Plan"):
        plan = st.session_state.ai_results['reorderPlan']
        st.subheader("AI Reorder Plan")
        st.write(f"**Mode:** {plan['mode']}")
        st.write(f"**Total Investment:** ₹{plan['totalInvestment']:.0f}")
        
        if plan['items']:
            df = pd.DataFrame(plan['items'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No reorder needed at this time")
        st.divider()
    
    # Inventory table
    df = pd.DataFrame(data['inventory'])
    df['margin'] = ((df['sellingPrice'] - df['costPrice']) / df['sellingPrice'] * 100).round(1)
    st.dataframe(df[['name', 'category', 'quantity', 'costPrice', 'sellingPrice', 'margin']], use_container_width=True)

def show_sales():
    st.title("💰 Sales History")
    
    if not st.session_state.shop_data:
        st.info("👈 Load demo data first")
        return
    
    data = st.session_state.shop_data
    df = pd.DataFrame(data['salesHistory'][-20:])
    st.dataframe(df[['saleId', 'customerName', 'totalAmount', 'paymentMethod', 'timestamp']], use_container_width=True)

def show_udhaar():
    st.title("📝 Udhaar Management")
    
    if not st.session_state.shop_data:
        st.info("👈 Load demo data first")
        return
    
    data = st.session_state.shop_data
    
    # Show credit scores if AI results available
    if st.session_state.ai_results and st.button("🤖 Show Credit Risk Scores"):
        scores = list(st.session_state.ai_results['creditScores'].values())
        st.subheader("Credit Risk Scores")
        df = pd.DataFrame(scores)
        st.dataframe(df, use_container_width=True)
        st.divider()
    
    # Udhaar table
    df = pd.DataFrame(data['udhaarRecords'])
    st.dataframe(df[['customerName', 'amount', 'paidAmount', 'remainingAmount', 'status']], use_container_width=True)

def show_forecast():
    st.title("📈 Demand Forecast")
    
    if not st.session_state.shop_data:
        st.info("👈 Load demo data first")
        return
    
    if not st.session_state.ai_results:
        st.info("👈 Run AI analysis first")
        return
    
    forecasts = st.session_state.ai_results['forecasts']
    
    for item_id, forecast in list(forecasts.items())[:5]:
        with st.expander(f"📊 {forecast['itemName']}", expanded=True):
            st.write(f"**Current Stock:** {forecast['currentStock']} | **7-Day Forecast:** {forecast['totalForecast']} units")
            st.write(f"**Recommendation:** {forecast['recommendation']}")
            
            df = pd.DataFrame(forecast['forecast'])
            st.line_chart(df.set_index('date')['predictedQuantity'])

def show_pricing():
    st.title("💵 Pricing Intelligence")
    
    if not st.session_state.shop_data:
        st.info("👈 Load demo data first")
        return
    
    if not st.session_state.ai_results:
        st.info("👈 Run AI analysis first")
        return
    
    recommendations = list(st.session_state.ai_results['pricingRecommendations'].values())
    df = pd.DataFrame(recommendations)
    st.dataframe(df, use_container_width=True)

# Main app logic
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
