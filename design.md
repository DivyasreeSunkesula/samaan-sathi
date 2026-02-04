# Samaan Sathi AI – System Design

## High-Level Architecture

Samaan Sathi AI follows a modular, AI-assisted client–server architecture designed for scale, accessibility, and reliability for small retailers.

At a high level:  
- Shop owners interact via a web app frontend (text and optional image input for bills).  
- Requests are routed through a secure backend API layer.  
- The backend orchestrates AI services, data ingestion, and business logic.  
- Responses are generated using AI models grounded in historical sales data, local trends, and business rules.  
- The system is designed to operate with mock/synthetic sales data during the hackathon while remaining production-ready for real retail integration.  

---

## Major Components

### 1. Frontend (User Interface Layer)
**Role:** Shop owner interaction, simplicity, and input/output handling.

- Text-based UI for stock, pricing, and sales recommendations (primary)  
- Optional image upload for bill/receipt ingestion (OCR)  
- Simple dashboards showing actionable insights (stock alerts, price suggestions)  
- Language selection (multilingual support)  
- Low cognitive load design for non-technical users  

**Key Focus:** Accessibility, simplicity, minimal steps to actionable recommendations.

---

### 2. Backend
**Role:** Central control plane for logic, security, and AI orchestration.

- API gateway for frontend requests  
- Session and state management for shop/store context  
- Validation and sanitization of CSV, POS, or bill data  
- Integration with AI services for forecasting, pricing, and recommendations  

**Key Focus:** Reliability, scalability, and clear separation of concerns.

---

### 3. AI Services
**Role:** Understanding data, generating actionable recommendations, and explaining insights.

- **Time-series forecasting** for short-term demand (7–14 days)  
- **Price elasticity modeling** to suggest optimal pricing  
- **OCR + NLP** to extract sales info from bills or CSV uploads  
- **LLM explanation layer** for human-readable recommendation summaries  
- Confidence scoring to guide shop owners on decision certainty  

**Key Focus:** Accuracy, explainability, trustworthiness of AI recommendations.

---

### 4. Knowledge & Data Layer
**Role:** Trusted source of truth for recommendations.

- Historical sales data from shop CSVs or POS  
- Local trends and festival calendars  
- Mock inventory and sales datasets for testing  
- Configurable business rules (e.g., minimum stock limits, expiry alerts)  

**Key Focus:** Data accuracy, consistency, and traceability for reliable insights.

---

## System & User Flows

### Flow 1: Inventory Recommendation
1. Shop owner uploads CSV or bill image.  
2. Backend validates input and extracts sales data.  
3. AI forecasts next 7–14 days demand and flags slow/fast-moving items.  
4. Frontend displays actionable recommendations:  
   - “Order 30 units of item X”  
   - “Reduce price of item Y by ₹2”  

---

### Flow 2: Pricing Suggestion
1. Backend fetches historical sales and competitor/local trends.  
2. AI calculates price sensitivity and potential impact.  
3. Recommendations are displayed in simple terms with reasoning.  

---

### Flow 3: Alerts & Notifications
- Dead stock / expiry alerts generated based on historical sales velocity.  
- Seasonal/festival spikes highlighted for proactive stocking.  
- Notifications delivered via app or email (optional).  

---

### Flow 4: Human Escalation (Optional)
- If AI confidence is low, alerts shop owner to:  
  - Review recommendation manually  
  - Contact supplier or mentor for guidance  
- Ensures trust in AI-generated insights.

---

## AWS / Cloud Integration

AWS is used strategically to ensure scalability, reliability, and security:

- **Amazon API Gateway** – Entry point for frontend requests  
- **AWS Lambda** – Serverless backend logic and orchestration  
- **Amazon Bedrock / SageMaker** – AI model hosting for forecasting and recommendations  
- **Amazon OpenSearch / Vector Store** – Hybrid search for trend retrieval and context  
- **Amazon S3** – Storage for CSV uploads, bill images, and mock datasets  
- **Amazon Polly (Optional)** – Voice output for accessibility  
- **Amazon Transcribe (Optional)** – Bill image or voice-to-text conversion  

**Why AWS:** Scalable, secure, cost-effective, production-ready.

---

## Technical Logic

1. User input is validated and classified (intent: stock/pricing; shop/store context).  
2. OCR/NLP extracts structured data from CSV or bill images.  
3. Relevant historical sales data and local trend information are retrieved.  
4. AI models generate actionable recommendations and confidence scores.  
5. Human-readable explanations are produced by the LLM layer.  
6. Backend delivers recommendations to frontend.  
7. Low-confidence cases trigger alerts for manual review.  

**Design Goals:**
- **Scalable:** Supports thousands of small retailers concurrently  
- **Trustworthy:** Recommendations grounded in historical data and trends  
- **Inclusive:** Language support and simple UI for non-technical users  
- **Production-ready:** Operates on mock data with production-ready architecture  

---

**Samaan Sathi AI is designed not just as a recommendation engine, but as a dependable AI retail companion that empowers kirana and MSME shop owners with actionable insights for smarter inventory and pricing decisions.**
