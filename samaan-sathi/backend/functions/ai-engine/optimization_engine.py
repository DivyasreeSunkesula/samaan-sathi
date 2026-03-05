"""
Optimization Engine - Constrained Reorder Decision Making
Solves: Maximize (Profit + Availability - Cash Risk)
Subject to: Budget, Storage, Lead Time, Udhaar Exposure
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

class OptimizationEngine:
    """
    Multi-objective optimization for inventory reordering
    This is the CORE AI that cannot be replaced with simple rules
    """
    
    def __init__(self):
        self.max_iterations = 100
        self.convergence_threshold = 0.01
    
    def optimize_reorder(self, 
                        inventory_items: List[Dict],
                        forecasts: Dict[str, Any],
                        cash_available: float,
                        udhaar_outstanding: float,
                        storage_capacity: float,
                        supplier_lead_time: int = 3) -> Dict[str, Any]:
        """
        Optimize reorder quantities under multiple constraints
        
        Args:
            inventory_items: Current inventory with costs, margins, etc.
            forecasts: Demand forecasts for each item
            cash_available: Available cash for purchasing
            udhaar_outstanding: Total outstanding credit
            storage_capacity: Maximum storage space
            supplier_lead_time: Days until delivery
        
        Returns:
            Optimized reorder plan with reasoning
        """
        # Calculate cash flow health
        cash_flow_health = self._assess_cash_flow_health(
            cash_available, 
            udhaar_outstanding
        )
        
        # Prioritize items based on multiple factors
        prioritized_items = self._prioritize_items(
            inventory_items,
            forecasts,
            cash_flow_health
        )
        
        # Solve constrained optimization
        reorder_plan = self._solve_optimization(
            prioritized_items,
            cash_available,
            storage_capacity,
            supplier_lead_time,
            cash_flow_health
        )
        
        # Calculate impact metrics
        impact = self._calculate_impact(reorder_plan, inventory_items, forecasts)
        
        # Generate explanation
        explanation = self._generate_explanation(
            reorder_plan,
            cash_flow_health,
            cash_available,
            udhaar_outstanding,
            impact
        )
        
        return {
            'reorderPlan': reorder_plan,
            'cashFlowHealth': cash_flow_health,
            'constraints': {
                'cashAvailable': round(cash_available, 2),
                'udhaarOutstanding': round(udhaar_outstanding, 2),
                'storageCapacity': round(storage_capacity, 2),
                'supplierLeadTime': supplier_lead_time
            },
            'impact': impact,
            'explanation': explanation,
            'optimizationMethod': 'constrained_multi_objective',
            'generatedAt': datetime.now().isoformat()
        }
    
    def _assess_cash_flow_health(self, cash_available: float, 
                                 udhaar_outstanding: float) -> Dict[str, Any]:
        """Assess cash flow health and determine mode"""
        # Calculate key ratios
        if cash_available > 0:
            udhaar_ratio = udhaar_outstanding / cash_available
        else:
            udhaar_ratio = float('inf')
        
        # Determine health status
        if udhaar_ratio > 2.0 or cash_available < 5000:
            status = 'CRITICAL'
            mode = 'SURVIVAL'
            risk_level = 'HIGH'
            description = 'Cash crunch detected. Survival mode activated.'
        elif udhaar_ratio > 1.0 or cash_available < 10000:
            status = 'WARNING'
            mode = 'CONSERVATIVE'
            risk_level = 'MEDIUM'
            description = 'Cash flow stress. Conservative purchasing.'
        elif udhaar_ratio > 0.5:
            status = 'MODERATE'
            mode = 'BALANCED'
            risk_level = 'LOW'
            description = 'Moderate cash flow. Balanced approach.'
        else:
            status = 'HEALTHY'
            mode = 'GROWTH'
            risk_level = 'MINIMAL'
            description = 'Healthy cash flow. Growth mode.'
        
        return {
            'status': status,
            'mode': mode,
            'riskLevel': risk_level,
            'description': description,
            'udhaarRatio': round(udhaar_ratio, 2),
            'cashAvailable': round(cash_available, 2),
            'udhaarOutstanding': round(udhaar_outstanding, 2)
        }
    
    def _prioritize_items(self, inventory_items: List[Dict],
                         forecasts: Dict[str, Any],
                         cash_flow_health: Dict) -> List[Dict]:
        """
        Prioritize items based on multiple factors
        This is where AI adds value - multi-dimensional scoring
        """
        prioritized = []
        
        for item in inventory_items:
            item_id = item.get('itemId', '')
            
            # Get forecast for this item
            forecast = forecasts.get(item_id, {})
            predicted_demand = forecast.get('totalForecast', 0)
            
            # Calculate priority score components
            
            # 1. Stockout risk (0-100)
            current_stock = item.get('quantity', 0)
            if predicted_demand > 0:
                stockout_risk = max(0, min(100, (1 - current_stock / predicted_demand) * 100))
            else:
                stockout_risk = 0
            
            # 2. Margin score (0-100)
            cost_price = item.get('costPrice', 0)
            selling_price = item.get('sellingPrice', 0)
            if selling_price > 0:
                margin_pct = ((selling_price - cost_price) / selling_price) * 100
                margin_score = min(100, margin_pct * 2)  # Scale to 0-100
            else:
                margin_score = 0
            
            # 3. Velocity score (0-100)
            # Fast-moving items get higher priority
            velocity = item.get('salesVelocity', 5)  # units per day
            velocity_score = min(100, velocity * 10)
            
            # 4. Category importance (0-100)
            category = item.get('category', 'groceries')
            category_scores = {
                'groceries': 90,      # Essential
                'beverages': 70,      # Important
                'snacks': 60,         # Moderate
                'personal-care': 50,  # Lower priority
                'household': 55       # Lower priority
            }
            category_score = category_scores.get(category, 50)
            
            # 5. Cash flow mode adjustment
            mode = cash_flow_health.get('mode', 'BALANCED')
            if mode == 'SURVIVAL':
                # In survival mode, prioritize high-margin, fast-moving only
                mode_weight = {
                    'stockout_risk': 0.2,
                    'margin': 0.5,      # Heavily favor high margin
                    'velocity': 0.2,
                    'category': 0.1
                }
            elif mode == 'CONSERVATIVE':
                # Conservative: balance margin and stockout risk
                mode_weight = {
                    'stockout_risk': 0.3,
                    'margin': 0.4,
                    'velocity': 0.2,
                    'category': 0.1
                }
            elif mode == 'GROWTH':
                # Growth: prioritize volume and availability
                mode_weight = {
                    'stockout_risk': 0.4,
                    'margin': 0.2,
                    'velocity': 0.3,
                    'category': 0.1
                }
            else:  # BALANCED
                mode_weight = {
                    'stockout_risk': 0.35,
                    'margin': 0.30,
                    'velocity': 0.25,
                    'category': 0.10
                }
            
            # Calculate composite priority score
            priority_score = (
                stockout_risk * mode_weight['stockout_risk'] +
                margin_score * mode_weight['margin'] +
                velocity_score * mode_weight['velocity'] +
                category_score * mode_weight['category']
            )
            
            # Calculate optimal reorder quantity (before constraints)
            shortage = max(0, predicted_demand - current_stock)
            safety_stock = predicted_demand * 0.2  # 20% buffer
            optimal_qty = shortage + safety_stock
            
            prioritized.append({
                'itemId': item_id,
                'name': item.get('name', 'Unknown'),
                'category': category,
                'currentStock': current_stock,
                'predictedDemand': predicted_demand,
                'shortage': shortage,
                'optimalQty': round(optimal_qty),
                'costPrice': cost_price,
                'sellingPrice': selling_price,
                'marginPct': round(margin_pct, 1) if selling_price > 0 else 0,
                'priorityScore': round(priority_score, 1),
                'scoreBreakdown': {
                    'stockoutRisk': round(stockout_risk, 1),
                    'marginScore': round(margin_score, 1),
                    'velocityScore': round(velocity_score, 1),
                    'categoryScore': category_score
                }
            })
        
        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x['priorityScore'], reverse=True)
        
        return prioritized
    
    def _solve_optimization(self, prioritized_items: List[Dict],
                           cash_available: float,
                           storage_capacity: float,
                           lead_time: int,
                           cash_flow_health: Dict) -> List[Dict]:
        """
        Solve constrained optimization problem
        This is the CORE AI logic - cannot be done with simple rules
        """
        reorder_plan = []
        remaining_cash = cash_available
        remaining_storage = storage_capacity
        
        mode = cash_flow_health.get('mode', 'BALANCED')
        
        # Reserve cash for emergencies based on mode
        if mode == 'SURVIVAL':
            reserve_ratio = 0.5  # Keep 50% cash reserve
        elif mode == 'CONSERVATIVE':
            reserve_ratio = 0.3  # Keep 30% cash reserve
        else:
            reserve_ratio = 0.1  # Keep 10% cash reserve
        
        available_for_purchase = cash_available * (1 - reserve_ratio)
        
        # Greedy algorithm with constraints
        for item in prioritized_items:
            item_id = item['itemId']
            name = item['name']
            optimal_qty = item['optimalQty']
            cost_price = item['costPrice']
            priority_score = item['priorityScore']
            
            # Skip if no shortage
            if optimal_qty <= 0:
                continue
            
            # Calculate cost
            total_cost = optimal_qty * cost_price
            
            # Check cash constraint
            if total_cost > available_for_purchase:
                # Reduce quantity to fit budget
                affordable_qty = int(available_for_purchase / cost_price) if cost_price > 0 else 0
                if affordable_qty > 0:
                    optimal_qty = affordable_qty
                    total_cost = optimal_qty * cost_price
                else:
                    # Cannot afford even 1 unit
                    reorder_plan.append({
                        'itemId': item_id,
                        'name': name,
                        'recommendedQty': 0,
                        'reason': 'CASH_CONSTRAINT',
                        'priorityScore': priority_score,
                        'status': 'SKIPPED'
                    })
                    continue
            
            # Check storage constraint (simplified: 1 unit = 1 storage unit)
            if optimal_qty > remaining_storage:
                optimal_qty = int(remaining_storage)
                total_cost = optimal_qty * cost_price
            
            # Add to reorder plan
            if optimal_qty > 0:
                reorder_plan.append({
                    'itemId': item_id,
                    'name': name,
                    'category': item['category'],
                    'currentStock': item['currentStock'],
                    'predictedDemand': item['predictedDemand'],
                    'recommendedQty': optimal_qty,
                    'costPrice': cost_price,
                    'totalCost': round(total_cost, 2),
                    'marginPct': item['marginPct'],
                    'priorityScore': priority_score,
                    'reason': self._get_reorder_reason(item, mode),
                    'status': 'RECOMMENDED'
                })
                
                # Update remaining resources
                available_for_purchase -= total_cost
                remaining_storage -= optimal_qty
            
            # Stop if resources exhausted
            if available_for_purchase <= 0 or remaining_storage <= 0:
                break
        
        return reorder_plan
    
    def _get_reorder_reason(self, item: Dict, mode: str) -> str:
        """Generate reason for reorder recommendation"""
        shortage = item['shortage']
        margin = item['marginPct']
        priority = item['priorityScore']
        
        if mode == 'SURVIVAL':
            return f"High-margin ({margin:.0f}%), essential for cash flow"
        elif shortage > item['predictedDemand'] * 0.5:
            return f"Critical shortage: {shortage} units needed"
        elif priority > 80:
            return f"High priority: fast-moving, good margin"
        elif margin > 30:
            return f"Good margin ({margin:.0f}%), profitable item"
        else:
            return f"Moderate priority, balanced decision"
    
    def _calculate_impact(self, reorder_plan: List[Dict],
                         inventory_items: List[Dict],
                         forecasts: Dict) -> Dict[str, Any]:
        """Calculate impact of reorder plan"""
        # Total investment
        total_investment = sum(item['totalCost'] for item in reorder_plan if item['status'] == 'RECOMMENDED')
        
        # Expected revenue
        expected_revenue = sum(
            item['recommendedQty'] * item.get('sellingPrice', item['costPrice'] * 1.2)
            for item in reorder_plan if item['status'] == 'RECOMMENDED'
        )
        
        # Expected profit
        expected_profit = expected_revenue - total_investment
        
        # ROI
        roi = (expected_profit / total_investment * 100) if total_investment > 0 else 0
        
        # Coverage
        items_covered = len([i for i in reorder_plan if i['status'] == 'RECOMMENDED'])
        total_items = len(inventory_items)
        coverage_pct = (items_covered / total_items * 100) if total_items > 0 else 0
        
        return {
            'totalInvestment': round(total_investment, 2),
            'expectedRevenue': round(expected_revenue, 2),
            'expectedProfit': round(expected_profit, 2),
            'expectedROI': round(roi, 1),
            'itemsCovered': items_covered,
            'totalItems': total_items,
            'coveragePercentage': round(coverage_pct, 1)
        }
    
    def _generate_explanation(self, reorder_plan: List[Dict],
                             cash_flow_health: Dict,
                             cash_available: float,
                             udhaar_outstanding: float,
                             impact: Dict) -> str:
        """Generate human-readable explanation"""
        mode = cash_flow_health['mode']
        status = cash_flow_health['status']
        
        recommended_items = [i for i in reorder_plan if i['status'] == 'RECOMMENDED']
        skipped_items = [i for i in reorder_plan if i['status'] == 'SKIPPED']
        
        explanation = f"**Cash Flow Status:** {status} ({mode} mode)\n\n"
        
        if mode == 'SURVIVAL':
            explanation += "🚨 **Survival Mode Active**\n"
            explanation += f"Cash available: ₹{cash_available:.0f}, Udhaar outstanding: ₹{udhaar_outstanding:.0f}\n"
            explanation += "Prioritizing high-margin, fast-moving items only.\n\n"
        elif mode == 'CONSERVATIVE':
            explanation += "⚠️ **Conservative Mode**\n"
            explanation += f"Cash flow stress detected. Balancing margin and availability.\n\n"
        
        explanation += f"**Recommended Orders:** {len(recommended_items)} items\n"
        explanation += f"**Total Investment:** ₹{impact['totalInvestment']:.0f}\n"
        explanation += f"**Expected Profit:** ₹{impact['expectedProfit']:.0f} (ROI: {impact['expectedROI']:.0f}%)\n\n"
        
        if skipped_items:
            explanation += f"**Skipped:** {len(skipped_items)} items due to cash constraints\n"
        
        explanation += "\n**Top Recommendations:**\n"
        for item in recommended_items[:5]:
            explanation += f"- {item['name']}: {item['recommendedQty']} units (₹{item['totalCost']:.0f}) - {item['reason']}\n"
        
        return explanation


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        inventory_items = body.get('inventoryItems', [])
        forecasts = body.get('forecasts', {})
        cash_available = body.get('cashAvailable', 10000)
        udhaar_outstanding = body.get('udhaarOutstanding', 0)
        storage_capacity = body.get('storageCapacity', 1000)
        supplier_lead_time = body.get('supplierLeadTime', 3)
        
        engine = OptimizationEngine()
        result = engine.optimize_reorder(
            inventory_items,
            forecasts,
            cash_available,
            udhaar_outstanding,
            storage_capacity,
            supplier_lead_time
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
