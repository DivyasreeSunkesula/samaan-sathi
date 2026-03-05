"""
Cash Flow Simulator - Monte Carlo Simulation for 14-day Cash Flow Projection
Predicts cash crunch scenarios and triggers survival mode
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class CashFlowSimulator:
    """
    Simulates cash flow scenarios using Monte Carlo method
    Detects: udhaar unpaid risk, demand spikes, supplier payments
    """
    
    def __init__(self):
        self.simulation_runs = 1000  # Monte Carlo iterations
        self.confidence_level = 0.95
    
    def simulate_cash_flow(self,
                          current_cash: float,
                          udhaar_outstanding: float,
                          udhaar_records: List[Dict],
                          inventory_items: List[Dict],
                          forecasts: Dict[str, Any],
                          supplier_payments: List[Dict] = None,
                          days: int = 14) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for cash flow over next N days
        
        Args:
            current_cash: Available cash
            udhaar_outstanding: Total outstanding credit
            udhaar_records: Individual udhaar transactions
            inventory_items: Current inventory
            forecasts: Demand forecasts
            supplier_payments: Upcoming supplier payments
            days: Simulation period
        
        Returns:
            Simulation results with risk assessment
        """
        # Run Monte Carlo simulations
        scenarios = []
        for _ in range(self.simulation_runs):
            scenario = self._simulate_single_scenario(
                current_cash,
                udhaar_outstanding,
                udhaar_records,
                inventory_items,
                forecasts,
                supplier_payments or [],
                days
            )
            scenarios.append(scenario)
        
        # Analyze results
        analysis = self._analyze_scenarios(scenarios, current_cash)
        
        # Determine if survival mode needed
        survival_mode = self._assess_survival_mode(analysis, current_cash, udhaar_outstanding)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            analysis,
            survival_mode,
            current_cash,
            udhaar_outstanding,
            udhaar_records
        )
        
        return {
            'currentCash': round(current_cash, 2),
            'udhaarOutstanding': round(udhaar_outstanding, 2),
            'simulationDays': days,
            'simulationRuns': self.simulation_runs,
            'analysis': analysis,
            'survivalMode': survival_mode,
            'recommendations': recommendations,
            'dailyProjections': self._get_daily_projections(scenarios, days),
            'generatedAt': datetime.now().isoformat()
        }
    
    def _simulate_single_scenario(self,
                                  current_cash: float,
                                  udhaar_outstanding: float,
                                  udhaar_records: List[Dict],
                                  inventory_items: List[Dict],
                                  forecasts: Dict,
                                  supplier_payments: List[Dict],
                                  days: int) -> Dict[str, Any]:
        """Simulate one possible scenario"""
        cash = current_cash
        daily_cash = [cash]
        
        for day in range(days):
            # Daily sales revenue (from forecasts with uncertainty)
            daily_revenue = self._simulate_daily_revenue(inventory_items, forecasts)
            
            # Udhaar collections (probabilistic)
            daily_collections = self._simulate_udhaar_collections(udhaar_records, day)
            
            # Operating expenses (random variation)
            daily_expenses = self._simulate_daily_expenses(current_cash)
            
            # Supplier payments (if due)
            supplier_payment = self._get_supplier_payment(supplier_payments, day)
            
            # Inventory purchases (simplified)
            inventory_purchase = self._simulate_inventory_purchase(cash, day)
            
            # Update cash
            cash += daily_revenue
            cash += daily_collections
            cash -= daily_expenses
            cash -= supplier_payment
            cash -= inventory_purchase
            
            daily_cash.append(cash)
        
        # Calculate metrics
        min_cash = min(daily_cash)
        final_cash = daily_cash[-1]
        cash_crunch_days = len([c for c in daily_cash if c < 1000])
        
        return {
            'finalCash': final_cash,
            'minCash': min_cash,
            'cashCrunchDays': cash_crunch_days,
            'dailyCash': daily_cash
        }
    
    def _simulate_daily_revenue(self, inventory_items: List[Dict], forecasts: Dict) -> float:
        """Simulate daily sales revenue with uncertainty"""
        total_revenue = 0
        
        for item in inventory_items[:20]:  # Sample top items
            item_id = item.get('itemId', '')
            selling_price = item.get('sellingPrice', 0)
            
            # Get forecast
            forecast = forecasts.get(item_id, {})
            avg_daily_demand = forecast.get('totalForecast', 5) / 7
            
            # Add uncertainty (±30%)
            actual_demand = avg_daily_demand * random.uniform(0.7, 1.3)
            
            # Revenue
            total_revenue += actual_demand * selling_price
        
        return total_revenue
    
    def _simulate_udhaar_collections(self, udhaar_records: List[Dict], day: int) -> float:
        """Simulate udhaar collections with probability"""
        collections = 0
        
        for record in udhaar_records:
            if record.get('status') == 'PENDING':
                outstanding = record.get('amount', 0) - record.get('paidAmount', 0)
                
                # Probability of payment increases over time
                payment_probability = min(0.15, day * 0.01)
                
                if random.random() < payment_probability:
                    # Partial or full payment
                    payment = outstanding * random.uniform(0.3, 1.0)
                    collections += payment
        
        return collections
    
    def _simulate_daily_expenses(self, current_cash: float) -> float:
        """Simulate daily operating expenses"""
        # Base expenses: 2-5% of current cash per day
        base_expense = current_cash * random.uniform(0.02, 0.05)
        
        # Random additional expenses (10% chance)
        if random.random() < 0.1:
            base_expense += random.uniform(500, 2000)
        
        return base_expense
    
    def _get_supplier_payment(self, supplier_payments: List[Dict], day: int) -> float:
        """Get supplier payment if due on this day"""
        for payment in supplier_payments:
            if payment.get('dueDay') == day:
                return payment.get('amount', 0)
        return 0
    
    def _simulate_inventory_purchase(self, cash: float, day: int) -> float:
        """Simulate inventory purchase (weekly)"""
        # Purchase every 7 days
        if day % 7 == 0 and cash > 5000:
            return cash * random.uniform(0.15, 0.25)
        return 0
    
    def _analyze_scenarios(self, scenarios: List[Dict], current_cash: float) -> Dict[str, Any]:
        """Analyze Monte Carlo results"""
        final_cash_values = [s['finalCash'] for s in scenarios]
        min_cash_values = [s['minCash'] for s in scenarios]
        crunch_days = [s['cashCrunchDays'] for s in scenarios]
        
        # Sort for percentile calculations
        final_cash_values.sort()
        min_cash_values.sort()
        
        # Calculate percentiles
        p5_final = final_cash_values[int(len(final_cash_values) * 0.05)]
        p50_final = final_cash_values[int(len(final_cash_values) * 0.50)]
        p95_final = final_cash_values[int(len(final_cash_values) * 0.95)]
        
        p5_min = min_cash_values[int(len(min_cash_values) * 0.05)]
        p50_min = min_cash_values[int(len(min_cash_values) * 0.50)]
        
        # Risk metrics
        cash_crunch_probability = len([c for c in min_cash_values if c < 1000]) / len(scenarios)
        negative_cash_probability = len([c for c in min_cash_values if c < 0]) / len(scenarios)
        avg_crunch_days = sum(crunch_days) / len(crunch_days)
        
        # Risk level
        if negative_cash_probability > 0.3 or cash_crunch_probability > 0.5:
            risk_level = 'CRITICAL'
        elif negative_cash_probability > 0.1 or cash_crunch_probability > 0.3:
            risk_level = 'HIGH'
        elif cash_crunch_probability > 0.1:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'riskLevel': risk_level,
            'cashCrunchProbability': round(cash_crunch_probability * 100, 1),
            'negativeCashProbability': round(negative_cash_probability * 100, 1),
            'avgCashCrunchDays': round(avg_crunch_days, 1),
            'projections': {
                'pessimistic': {
                    'finalCash': round(p5_final, 2),
                    'minCash': round(p5_min, 2)
                },
                'expected': {
                    'finalCash': round(p50_final, 2),
                    'minCash': round(p50_min, 2)
                },
                'optimistic': {
                    'finalCash': round(p95_final, 2),
                    'minCash': round(min_cash_values[-1], 2)
                }
            }
        }
    
    def _assess_survival_mode(self, analysis: Dict, current_cash: float, 
                             udhaar_outstanding: float) -> Dict[str, Any]:
        """Determine if survival mode should be activated"""
        risk_level = analysis['riskLevel']
        cash_crunch_prob = analysis['cashCrunchProbability']
        
        # Survival mode triggers
        triggers = []
        
        if risk_level in ['CRITICAL', 'HIGH']:
            triggers.append('High cash flow risk detected')
        
        if cash_crunch_prob > 30:
            triggers.append(f'{cash_crunch_prob:.0f}% chance of cash crunch')
        
        if udhaar_outstanding > current_cash * 1.5:
            triggers.append('Udhaar exposure too high')
        
        if current_cash < 5000:
            triggers.append('Critical cash level')
        
        activated = len(triggers) > 0
        
        if activated:
            # Survival mode actions
            actions = [
                'Reduce udhaar limits by 30%',
                'Pause low-margin inventory purchases',
                'Prioritize high-margin fast-moving items',
                'Accelerate udhaar collections',
                'Defer non-essential expenses'
            ]
        else:
            actions = []
        
        return {
            'activated': activated,
            'triggers': triggers,
            'actions': actions,
            'severity': risk_level
        }
    
    def _generate_recommendations(self, analysis: Dict, survival_mode: Dict,
                                 current_cash: float, udhaar_outstanding: float,
                                 udhaar_records: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        risk_level = analysis['riskLevel']
        
        if survival_mode['activated']:
            recommendations.append(f"🚨 SURVIVAL MODE ACTIVATED - {survival_mode['severity']} risk")
            recommendations.extend([f"• {action}" for action in survival_mode['actions']])
        
        # Udhaar-specific recommendations
        overdue_udhaar = sum(
            r.get('amount', 0) - r.get('paidAmount', 0)
            for r in udhaar_records
            if r.get('status') == 'OVERDUE'
        )
        
        if overdue_udhaar > current_cash * 0.3:
            recommendations.append(f"⚠️ ₹{overdue_udhaar:.0f} overdue. Follow up with customers immediately.")
        
        # Cash buffer recommendation
        if current_cash < 10000:
            recommendations.append("💰 Build cash buffer: Target ₹10,000 minimum reserve.")
        
        # Positive scenarios
        if risk_level == 'LOW':
            recommendations.append("✓ Cash flow healthy. Safe to pursue growth opportunities.")
        
        return recommendations
    
    def _get_daily_projections(self, scenarios: List[Dict], days: int) -> List[Dict]:
        """Get day-by-day projections"""
        daily_projections = []
        
        for day in range(days + 1):
            day_values = [s['dailyCash'][day] for s in scenarios]
            day_values.sort()
            
            p5 = day_values[int(len(day_values) * 0.05)]
            p50 = day_values[int(len(day_values) * 0.50)]
            p95 = day_values[int(len(day_values) * 0.95)]
            
            daily_projections.append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                'pessimistic': round(p5, 2),
                'expected': round(p50, 2),
                'optimistic': round(p95, 2)
            })
        
        return daily_projections


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        current_cash = body.get('currentCash', 10000)
        udhaar_outstanding = body.get('udhaarOutstanding', 0)
        udhaar_records = body.get('udhaarRecords', [])
        inventory_items = body.get('inventoryItems', [])
        forecasts = body.get('forecasts', {})
        supplier_payments = body.get('supplierPayments', [])
        days = body.get('days', 14)
        
        simulator = CashFlowSimulator()
        result = simulator.simulate_cash_flow(
            current_cash,
            udhaar_outstanding,
            udhaar_records,
            inventory_items,
            forecasts,
            supplier_payments,
            days
        )
        
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
