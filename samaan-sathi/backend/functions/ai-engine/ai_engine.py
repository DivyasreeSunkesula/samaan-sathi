"""
Unified AI Engine - Orchestrates all AI components
Main Lambda function for AI operations
"""
import json
from datetime import datetime
from typing import Dict, Any, List

# Import all AI engines
from forecast_engine import ForecastEngine
from credit_risk_scorer import CreditRiskScorer
from optimization_engine import OptimizationEngine
from cash_flow_simulator import CashFlowSimulator
from margin_optimizer import MarginOptimizer
from bedrock_explainer import BedrockExplainer


class AIEngine:
    """
    Unified AI Engine orchestrating all AI capabilities
    """
    
    def __init__(self):
        self.forecast_engine = ForecastEngine()
        self.credit_scorer = CreditRiskScorer()
        self.optimizer = OptimizationEngine()
        self.cash_flow_simulator = CashFlowSimulator()
        self.margin_optimizer = MarginOptimizer()
        self.explainer = BedrockExplainer()
    
    def run_daily_batch(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run daily batch AI processing for a shop
        This is the main AI workflow
        
        Args:
            shop_data: Complete shop data (inventory, sales, udhaar, etc.)
        
        Returns:
            Complete AI insights and recommendations
        """
        shop_id = shop_data.get('shopId', '')
        inventory_items = shop_data.get('inventory', [])
        sales_history = shop_data.get('salesHistory', [])
        udhaar_records = shop_data.get('udhaarRecords', [])
        cash_available = shop_data.get('cashAvailable', 10000)
        
        results = {
            'shopId': shop_id,
            'processedAt': datetime.now().isoformat(),
            'forecasts': {},
            'creditScores': {},
            'reorderPlan': {},
            'cashFlowSimulation': {},
            'pricingRecommendations': {},
            'insights': [],
            'alerts': []
        }
        
        # 1. Generate demand forecasts for all items
        print("Running demand forecasts...")
        forecasts = {}
        for item in inventory_items:
            try:
                forecast = self.forecast_engine.forecast_demand(
                    item, 
                    sales_history, 
                    days=7
                )
                forecasts[item['itemId']] = forecast
                
                # Check for critical alerts
                if forecast['currentStock'] < forecast['totalForecast'] * 0.3:
                    results['alerts'].append({
                        'type': 'STOCKOUT_RISK',
                        'severity': 'HIGH',
                        'message': f"⚠️ {item['name']} critically low. Need {forecast['totalForecast'] - forecast['currentStock']} units.",
                        'itemId': item['itemId']
                    })
            except Exception as e:
                print(f"Forecast error for {item.get('name')}: {e}")
        
        results['forecasts'] = forecasts
        
        # 2. Score all customers for credit risk
        print("Scoring customer credit risk...")
        customers = self._extract_customers(udhaar_records)
        credit_scores = {}
        customers_data = []
        
        for customer in customers:
            try:
                customer_udhaar = [u for u in udhaar_records if u.get('customerId') == customer['customerId']]
                customer_sales = [s for s in sales_history if s.get('customerId') == customer['customerId']]
                
                score = self.credit_scorer.score_customer(
                    customer,
                    customer_udhaar,
                    customer_sales
                )
                credit_scores[customer['customerId']] = score
                customers_data.append(score)
                
                # Check for high-risk alerts
                if score['riskCategory'] in ['HIGH_RISK', 'CHRONIC_DELAYER']:
                    if score['currentOutstanding'] > 0:
                        results['alerts'].append({
                            'type': 'HIGH_RISK_CUSTOMER',
                            'severity': 'MEDIUM',
                            'message': f"⚠️ {customer['customerName']} is {score['riskCategory']}. Outstanding: ₹{score['currentOutstanding']:.0f}",
                            'customerId': customer['customerId']
                        })
            except Exception as e:
                print(f"Credit scoring error for {customer.get('customerName')}: {e}")
        
        results['creditScores'] = credit_scores
        
        # Portfolio analysis
        if customers_data:
            try:
                portfolio = self.credit_scorer.cluster_customers(customers_data)
                results['portfolioAnalysis'] = portfolio
            except Exception as e:
                print(f"Portfolio analysis error: {e}")
        
        # 3. Run cash flow simulation
        print("Simulating cash flow...")
        try:
            udhaar_outstanding = sum(
                u.get('amount', 0) - u.get('paidAmount', 0)
                for u in udhaar_records
                if u.get('status') != 'PAID'
            )
            
            cash_flow = self.cash_flow_simulator.simulate_cash_flow(
                cash_available,
                udhaar_outstanding,
                udhaar_records,
                inventory_items,
                forecasts,
                days=14
            )
            results['cashFlowSimulation'] = cash_flow
            
            # Check for survival mode
            if cash_flow['survivalMode']['activated']:
                results['alerts'].append({
                    'type': 'SURVIVAL_MODE',
                    'severity': 'CRITICAL',
                    'message': f"🚨 SURVIVAL MODE ACTIVE: {cash_flow['survivalMode']['severity']} risk",
                    'triggers': cash_flow['survivalMode']['triggers']
                })
        except Exception as e:
            print(f"Cash flow simulation error: {e}")
        
        # 4. Optimize reorder plan
        print("Optimizing reorder plan...")
        try:
            reorder_plan = self.optimizer.optimize_reorder(
                inventory_items,
                forecasts,
                cash_available,
                udhaar_outstanding,
                storage_capacity=1000,
                supplier_lead_time=3
            )
            results['reorderPlan'] = reorder_plan
            
            # Generate insights
            if reorder_plan['cashFlowHealth']['status'] in ['CRITICAL', 'WARNING']:
                results['insights'].append({
                    'type': 'CASH_FLOW',
                    'priority': 'HIGH',
                    'message': reorder_plan['cashFlowHealth']['description']
                })
        except Exception as e:
            print(f"Reorder optimization error: {e}")
        
        # 5. Pricing recommendations (top 10 items by sales)
        print("Generating pricing recommendations...")
        pricing_recommendations = {}
        top_items = sorted(
            inventory_items,
            key=lambda x: x.get('salesVelocity', 0),
            reverse=True
        )[:10]
        
        for item in top_items:
            try:
                item_sales = [s for s in sales_history if any(
                    i.get('itemId') == item['itemId'] for i in s.get('items', [])
                )]
                
                # Determine inventory status
                forecast = forecasts.get(item['itemId'], {})
                if item['quantity'] > forecast.get('totalForecast', 0) * 2:
                    inventory_status = 'overstocked'
                elif item['quantity'] < forecast.get('totalForecast', 0) * 0.5:
                    inventory_status = 'understocked'
                else:
                    inventory_status = 'normal'
                
                pricing = self.margin_optimizer.optimize_pricing(
                    item,
                    item_sales,
                    inventory_status=inventory_status
                )
                pricing_recommendations[item['itemId']] = pricing
                
                # Alert for significant price changes
                if abs(pricing['priceChangePercent']) > 10:
                    results['insights'].append({
                        'type': 'PRICING',
                        'priority': 'MEDIUM',
                        'message': pricing['recommendation']
                    })
            except Exception as e:
                print(f"Pricing optimization error for {item.get('name')}: {e}")
        
        results['pricingRecommendations'] = pricing_recommendations
        
        # 6. Generate bundle recommendations
        print("Generating bundle recommendations...")
        try:
            bundles = self.margin_optimizer.recommend_bundles(
                inventory_items,
                sales_history,
                max_bundles=5
            )
            results['bundleRecommendations'] = bundles
        except Exception as e:
            print(f"Bundle recommendation error: {e}")
        
        # 7. Generate AI explanations for top insights
        print("Generating AI explanations...")
        try:
            # Explain top forecast
            if forecasts:
                top_forecast = max(forecasts.values(), key=lambda x: x.get('totalForecast', 0))
                explanation = self.explainer.explain_forecast(top_forecast, language='en')
                results['topForecastExplanation'] = explanation
            
            # Explain cash flow if critical
            if results.get('cashFlowSimulation'):
                if results['cashFlowSimulation']['analysis']['riskLevel'] in ['CRITICAL', 'HIGH']:
                    explanation = self.explainer.explain_cash_flow(
                        results['cashFlowSimulation'],
                        language='en'
                    )
                    results['cashFlowExplanation'] = explanation
            
            # Explain reorder plan
            if results.get('reorderPlan'):
                explanation = self.explainer.explain_reorder(
                    results['reorderPlan'],
                    language='en'
                )
                results['reorderExplanation'] = explanation
        except Exception as e:
            print(f"Explanation generation error: {e}")
        
        # 8. Generate summary insights
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _extract_customers(self, udhaar_records: List[Dict]) -> List[Dict]:
        """Extract unique customers from udhaar records"""
        customers = {}
        for record in udhaar_records:
            customer_id = record.get('customerId', '')
            if customer_id and customer_id not in customers:
                customers[customer_id] = {
                    'customerId': customer_id,
                    'customerName': record.get('customerName', 'Unknown'),
                    'phone': record.get('phone', ''),
                    'address': record.get('address', '')
                }
        return list(customers.values())
    
    def _generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate executive summary"""
        critical_alerts = len([a for a in results['alerts'] if a['severity'] == 'CRITICAL'])
        high_alerts = len([a for a in results['alerts'] if a['severity'] == 'HIGH'])
        
        # Calculate key metrics
        total_items = len(results['forecasts'])
        items_needing_restock = len([
            f for f in results['forecasts'].values()
            if f['currentStock'] < f['totalForecast']
        ])
        
        total_customers = len(results['creditScores'])
        high_risk_customers = len([
            c for c in results['creditScores'].values()
            if c['riskCategory'] in ['HIGH_RISK', 'CHRONIC_DELAYER']
        ])
        
        cash_flow_status = results.get('cashFlowSimulation', {}).get('analysis', {}).get('riskLevel', 'UNKNOWN')
        
        return {
            'criticalAlerts': critical_alerts,
            'highAlerts': high_alerts,
            'totalAlerts': len(results['alerts']),
            'itemsTracked': total_items,
            'itemsNeedingRestock': items_needing_restock,
            'customersTracked': total_customers,
            'highRiskCustomers': high_risk_customers,
            'cashFlowStatus': cash_flow_status,
            'aiEnginesRun': 6,
            'processingTime': 'Complete'
        }


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'batch')
        
        engine = AIEngine()
        
        if action == 'batch':
            # Daily batch processing
            shop_data = body.get('shopData', {})
            result = engine.run_daily_batch(shop_data)
        
        elif action == 'forecast':
            # Single forecast
            item = body.get('item', {})
            sales_history = body.get('salesHistory', [])
            days = body.get('days', 7)
            result = engine.forecast_engine.forecast_demand(item, sales_history, days)
        
        elif action == 'credit_score':
            # Single customer credit score
            customer = body.get('customer', {})
            udhaar_history = body.get('udhaarHistory', [])
            sales_history = body.get('salesHistory', [])
            result = engine.credit_scorer.score_customer(customer, udhaar_history, sales_history)
        
        elif action == 'optimize_reorder':
            # Reorder optimization
            inventory_items = body.get('inventoryItems', [])
            forecasts = body.get('forecasts', {})
            cash_available = body.get('cashAvailable', 10000)
            udhaar_outstanding = body.get('udhaarOutstanding', 0)
            result = engine.optimizer.optimize_reorder(
                inventory_items, forecasts, cash_available, udhaar_outstanding, 1000
            )
        
        elif action == 'simulate_cash_flow':
            # Cash flow simulation
            current_cash = body.get('currentCash', 10000)
            udhaar_outstanding = body.get('udhaarOutstanding', 0)
            udhaar_records = body.get('udhaarRecords', [])
            inventory_items = body.get('inventoryItems', [])
            forecasts = body.get('forecasts', {})
            result = engine.cash_flow_simulator.simulate_cash_flow(
                current_cash, udhaar_outstanding, udhaar_records, 
                inventory_items, forecasts, days=14
            )
        
        elif action == 'optimize_pricing':
            # Pricing optimization
            item = body.get('item', {})
            sales_history = body.get('salesHistory', [])
            inventory_status = body.get('inventoryStatus', 'normal')
            result = engine.margin_optimizer.optimize_pricing(
                item, sales_history, inventory_status=inventory_status
            )
        
        elif action == 'explain':
            # Generate explanation
            explanation_type = body.get('type', 'forecast')
            data = body.get('data', {})
            language = body.get('language', 'en')
            
            if explanation_type == 'forecast':
                result = engine.explainer.explain_forecast(data, language)
            elif explanation_type == 'credit_risk':
                result = engine.explainer.explain_credit_risk(data, language)
            elif explanation_type == 'reorder':
                result = engine.explainer.explain_reorder(data, language)
            elif explanation_type == 'cash_flow':
                result = engine.explainer.explain_cash_flow(data, language)
            elif explanation_type == 'pricing':
                result = engine.explainer.explain_pricing(data, language)
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid explanation type'})
                }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid action'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
