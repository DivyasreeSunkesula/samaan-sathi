# Samaan Sathi AI 🛒🤖  
**Give kirana stores the power of big-company retail analytics**

Samaan Sathi AI helps small shop owners make smarter **inventory, pricing, and udhaar (Kaatha)** decisions using simple, explainable AI — without complex dashboards or technical effort.

It brings **big-retail-grade intelligence** to small retailers in a form they can actually use.

---

## 🚩 Problem Statement

Small kirana and MSME retailers in India struggle with:
- No demand forecasting → stock-outs and overstocking
- Blind pricing → copied prices without understanding demand
- Inventory wastage → expiry and dead stock
- Untracked udhaar (Kaatha) → blocked cash flow
- No access to analytics → unlike organized retail chains

These challenges reduce margins, block working capital, and limit growth.

---

## 🎯 Who Is It For?

**Primary Users**
- Kirana and MSME shop owners across urban, semi-urban, and rural India  
- Limited technical knowledge, thin margins, low tolerance for complex tools  

**Core Need**
> *“Tell me what to stock, how much to stock, how to price — and how much money is stuck in udhaar — in simple terms.”*

---

## 🧠 Why AI?

Traditional rule-based systems fail with:
- Noisy and incomplete sales data  
- Informal credit practices  
- Highly variable demand  

Samaan Sathi AI uses AI to:
- Forecast short-term demand (7–14 days)
- Detect seasonality and festival spikes
- Estimate price sensitivity
- Analyze udhaar repayment patterns
- Generate human-readable explanations
- Deliver insights without technical complexity

---

## ✨ Key Features

### 📦 Inventory Forecasting
- Item-level demand forecasting (7–14 days)
- Optimal stock quantity recommendations
- Early detection of slow- and fast-moving items

### 💰 Pricing Recommendations
- Demand-based price suggestions
- Promotion and markdown identification
- Clear margin and sales impact explanations

### 📥 Sales & Data Ingestion
- CSV uploads
- Bill / receipt image uploads
- OCR + NLP for data extraction
- Designed to handle noisy or incomplete data

### 📒 Kaatha / Udhaar Management
- Customer-wise udhaar ledger
- Track udhaar entries and repayments
- View total outstanding udhaar
- Customer status: Paid / Pending / Overdue

### 🤖 AI-Powered Udhaar Intelligence
- Udhaar risk scoring (rule + ML)
- Overdue risk detection
- Suggested credit limits
- Cash-flow-aware inventory and pricing advice

### 🔔 Alerts & Notifications
- Dead stock / expiry alerts
- Stock-out risk alerts
- Seasonal demand alerts
- Udhaar overdue and high-risk customer alerts

---

## 🏗️ System Architecture (High Level)

- **Frontend:** Simple web UI for shop owners (text-first, multilingual)
- **Backend:** Secure API layer for orchestration and validation
- **AI Services:** Forecasting, pricing, OCR/NLP, udhaar risk scoring
- **Data Layer:** Sales history, inventory state, udhaar ledgers, local trends
- **Cloud:** AWS-based, scalable, production-ready

---

## 🔄 Core System Flows

### Inventory Recommendation
- Sales data uploaded
- AI forecasts demand
- Stock quantity suggestions shown

### Pricing Suggestion
- Historical sales and trends analyzed
- Price recommendations generated with reasoning

### Kaatha / Udhaar Flow
- Udhaar entries and repayments recorded
- Ledgers updated automatically
- AI evaluates overdue patterns
- Alerts and suggestions generated

---

## ☁️ Cloud & Tech Stack (Indicative)

- Amazon API Gateway
- AWS Lambda
- Amazon Bedrock / SageMaker
- Amazon OpenSearch / Vector Store
- Amazon S3
- Amazon Polly / Transcribe (optional)

---

## 📊 Success Metrics

**Business KPIs**
- Dead stock reduction
- Stock-out reduction
- Sales uplift
- Margin improvement
- Udhaar recovery rate
- Average udhaar cycle

**AI Metrics**
- Demand forecast accuracy (MAPE)
- Recommendation adoption rate
- Confidence score reliability
- Udhaar overdue risk identification accuracy

---

## 🧩 Design Principles

- Simple and explainable
- Advisory (not prescriptive or fintech)
- Built for low data and low bandwidth
- Inclusive and multilingual
- Production-ready, even with mock data

---

## 🚀 Vision

Samaan Sathi AI is not just an analytics tool.  
It is a **dependable AI companion** that helps kirana and MSME shop owners manage inventory, pricing, and udhaar intelligently — improving margins, cash flow, and confidence in everyday decisions.

---

## 📌 Status

This project is currently designed to:
- Work with mock/synthetic data
- Be demo-ready for hackathons
- Scale seamlessly to real-world retail integration
