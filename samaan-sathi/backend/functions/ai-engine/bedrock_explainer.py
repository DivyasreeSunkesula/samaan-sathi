"""
Bedrock Explainer - Human-Readable AI Explanations
Uses AWS Bedrock (Claude/Titan) with fallback to templates
"""
import json
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

class BedrockExplainer:
    """
    Generate human-readable explanations for AI decisions
    Fallback chain: Claude Sonnet → Titan → Template
    """
    
    def __init__(self):
        try:
            self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.bedrock_available = True
        except:
            self.bedrock_available = False
        
        # Model preferences
        self.models = {
            'claude': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'titan': 'amazon.titan-text-express-v1'
        }
    
    def explain_forecast(self, forecast_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """
        Explain demand forecast in human language
        
        Args:
            forecast_data: Forecast results
            language: 'en' or 'hi' (Hindi)
        
        Returns:
            Human-readable explanation
        """
        context = self._build_forecast_context(forecast_data)
        
        if language == 'hi':
            prompt = f"""तुम एक दुकानदार के सहायक हो। नीचे दिए गए मांग पूर्वानुमान को सरल हिंदी में समझाओ:

{context}

2-3 वाक्यों में समझाओ कि:
1. अगले दिनों में क्या बिकेगा
2. क्यों यह पूर्वानुमान है
3. दुकानदार को क्या करना चाहिए"""
        else:
            prompt = f"""You are a helpful assistant for a small shop owner. Explain this demand forecast in simple English:

{context}

In 2-3 sentences, explain:
1. What will sell in coming days
2. Why this forecast
3. What the shopkeeper should do"""
        
        explanation = self._generate_with_fallback(prompt, max_tokens=200)
        
        return {
            'type': 'forecast',
            'explanation': explanation,
            'language': language,
            'generatedAt': datetime.now().isoformat()
        }
    
    def explain_credit_risk(self, risk_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Explain credit risk score"""
        context = self._build_credit_context(risk_data)
        
        if language == 'hi':
            prompt = f"""तुम एक दुकानदार के सहायक हो। इस ग्राहक के उधार जोखिम को समझाओ:

{context}

2-3 वाक्यों में बताओ:
1. यह ग्राहक कितना विश्वसनीय है
2. कितना उधार देना सुरक्षित है
3. क्या सावधानी रखनी चाहिए"""
        else:
            prompt = f"""You are a helpful assistant for a small shop owner. Explain this customer's credit risk:

{context}

In 2-3 sentences, explain:
1. How reliable is this customer
2. How much credit is safe
3. What precautions to take"""
        
        explanation = self._generate_with_fallback(prompt, max_tokens=200)
        
        return {
            'type': 'credit_risk',
            'explanation': explanation,
            'language': language,
            'generatedAt': datetime.now().isoformat()
        }
    
    def explain_reorder(self, reorder_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Explain reorder recommendations"""
        context = self._build_reorder_context(reorder_data)
        
        if language == 'hi':
            prompt = f"""तुम एक दुकानदार के सहायक हो। इस स्टॉक ऑर्डर की सलाह को समझाओ:

{context}

2-3 वाक्यों में बताओ:
1. क्या ऑर्डर करना चाहिए
2. क्यों यह सलाह दी गई
3. इससे क्या फायदा होगा"""
        else:
            prompt = f"""You are a helpful assistant for a small shop owner. Explain this reorder recommendation:

{context}

In 2-3 sentences, explain:
1. What to order
2. Why this recommendation
3. What benefit it brings"""
        
        explanation = self._generate_with_fallback(prompt, max_tokens=200)
        
        return {
            'type': 'reorder',
            'explanation': explanation,
            'language': language,
            'generatedAt': datetime.now().isoformat()
        }
    
    def explain_cash_flow(self, cash_flow_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Explain cash flow simulation"""
        context = self._build_cash_flow_context(cash_flow_data)
        
        if language == 'hi':
            prompt = f"""तुम एक दुकानदार के सहायक हो। इस नकदी प्रवाह स्थिति को समझाओ:

{context}

2-3 वाक्यों में बताओ:
1. नकदी की स्थिति कैसी है
2. क्या खतरा है
3. क्या करना चाहिए"""
        else:
            prompt = f"""You are a helpful assistant for a small shop owner. Explain this cash flow situation:

{context}

In 2-3 sentences, explain:
1. How is the cash situation
2. What risks exist
3. What should be done"""
        
        explanation = self._generate_with_fallback(prompt, max_tokens=200)
        
        return {
            'type': 'cash_flow',
            'explanation': explanation,
            'language': language,
            'generatedAt': datetime.now().isoformat()
        }
    
    def explain_pricing(self, pricing_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Explain pricing recommendation"""
        context = self._build_pricing_context(pricing_data)
        
        if language == 'hi':
            prompt = f"""तुम एक दुकानदार के सहायक हो। इस कीमत की सलाह को समझाओ:

{context}

2-3 वाक्यों में बताओ:
1. कीमत बढ़ानी या घटानी चाहिए
2. क्यों यह बदलाव करना चाहिए
3. इससे कितना फायदा होगा"""
        else:
            prompt = f"""You are a helpful assistant for a small shop owner. Explain this pricing recommendation:

{context}

In 2-3 sentences, explain:
1. Should price increase or decrease
2. Why make this change
3. How much benefit expected"""
        
        explanation = self._generate_with_fallback(prompt, max_tokens=200)
        
        return {
            'type': 'pricing',
            'explanation': explanation,
            'language': language,
            'generatedAt': datetime.now().isoformat()
        }
    
    def _generate_with_fallback(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate explanation with fallback chain"""
        # Try Claude first
        if self.bedrock_available:
            try:
                response = self._call_claude(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"Claude failed: {e}")
        
        # Try Titan
        if self.bedrock_available:
            try:
                response = self._call_titan(prompt, max_tokens)
                if response:
                    return response
            except Exception as e:
                print(f"Titan failed: {e}")
        
        # Fallback to template
        return self._template_fallback(prompt)
    
    def _call_claude(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Call Claude Sonnet via Bedrock"""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        })
        
        response = self.bedrock.invoke_model(
            modelId=self.models['claude'],
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _call_titan(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Call Titan via Bedrock"""
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": 0.7,
                "topP": 0.9
            }
        })
        
        response = self.bedrock.invoke_model(
            modelId=self.models['titan'],
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['results'][0]['outputText']
    
    def _template_fallback(self, prompt: str) -> str:
        """Template-based fallback when Bedrock unavailable"""
        # Extract key info from prompt
        if 'forecast' in prompt.lower() or 'मांग' in prompt:
            return "Based on past sales and seasonal patterns, we predict demand for this item. Stock accordingly to avoid shortages."
        elif 'credit' in prompt.lower() or 'उधार' in prompt:
            return "This customer's payment history and behavior determine their credit score. Higher scores mean safer credit."
        elif 'reorder' in prompt.lower() or 'ऑर्डर' in prompt:
            return "This recommendation balances your cash, storage, and demand forecast to optimize profit."
        elif 'cash' in prompt.lower() or 'नकदी' in prompt:
            return "Cash flow simulation shows potential risks. Take action to maintain healthy cash reserves."
        elif 'pric' in prompt.lower() or 'कीमत' in prompt:
            return "Price optimization considers demand elasticity and margins to maximize profit."
        else:
            return "AI analysis complete. Follow the recommendations for best results."
    
    def _build_forecast_context(self, data: Dict) -> str:
        """Build context for forecast explanation"""
        item_name = data.get('itemName', 'Item')
        total_forecast = data.get('totalForecast', 0)
        current_stock = data.get('currentStock', 0)
        trend = data.get('trend', 'stable')
        
        return f"""Item: {item_name}
Current Stock: {current_stock} units
Predicted Demand (7 days): {total_forecast} units
Trend: {trend}
Shortage: {max(0, total_forecast - current_stock)} units"""
    
    def _build_credit_context(self, data: Dict) -> str:
        """Build context for credit risk explanation"""
        customer_name = data.get('customerName', 'Customer')
        risk_score = data.get('riskScore', 0)
        risk_category = data.get('riskCategory', 'MODERATE_RISK')
        credit_limit = data.get('recommendedCreditLimit', 0)
        outstanding = data.get('currentOutstanding', 0)
        
        return f"""Customer: {customer_name}
Risk Score: {risk_score}/100
Category: {risk_category}
Recommended Credit Limit: ₹{credit_limit}
Current Outstanding: ₹{outstanding}"""
    
    def _build_reorder_context(self, data: Dict) -> str:
        """Build context for reorder explanation"""
        cash_status = data.get('cashFlowHealth', {}).get('status', 'MODERATE')
        total_investment = data.get('impact', {}).get('totalInvestment', 0)
        expected_profit = data.get('impact', {}).get('expectedProfit', 0)
        items_count = len(data.get('reorderPlan', []))
        
        return f"""Cash Flow Status: {cash_status}
Items to Order: {items_count}
Total Investment: ₹{total_investment}
Expected Profit: ₹{expected_profit}"""
    
    def _build_cash_flow_context(self, data: Dict) -> str:
        """Build context for cash flow explanation"""
        current_cash = data.get('currentCash', 0)
        risk_level = data.get('analysis', {}).get('riskLevel', 'MEDIUM')
        crunch_probability = data.get('analysis', {}).get('cashCrunchProbability', 0)
        survival_mode = data.get('survivalMode', {}).get('activated', False)
        
        return f"""Current Cash: ₹{current_cash}
Risk Level: {risk_level}
Cash Crunch Probability: {crunch_probability}%
Survival Mode: {'ACTIVE' if survival_mode else 'INACTIVE'}"""
    
    def _build_pricing_context(self, data: Dict) -> str:
        """Build context for pricing explanation"""
        item_name = data.get('itemName', 'Item')
        current_price = data.get('currentPrice', 0)
        optimal_price = data.get('optimalPrice', 0)
        profit_change = data.get('impact', {}).get('changes', {}).get('profitChange', 0)
        
        return f"""Item: {item_name}
Current Price: ₹{current_price}
Optimal Price: ₹{optimal_price}
Expected Profit Change: ₹{profit_change}"""


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        explanation_type = body.get('type', 'forecast')
        data = body.get('data', {})
        language = body.get('language', 'en')
        
        explainer = BedrockExplainer()
        
        if explanation_type == 'forecast':
            result = explainer.explain_forecast(data, language)
        elif explanation_type == 'credit_risk':
            result = explainer.explain_credit_risk(data, language)
        elif explanation_type == 'reorder':
            result = explainer.explain_reorder(data, language)
        elif explanation_type == 'cash_flow':
            result = explainer.explain_cash_flow(data, language)
        elif explanation_type == 'pricing':
            result = explainer.explain_pricing(data, language)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid explanation type'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
