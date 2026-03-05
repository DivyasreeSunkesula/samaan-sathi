"""
Margin Optimization Engine - Price Elasticity & Optimal Pricing
Learns price sensitivity and suggests optimal pricing strategies
"""
import json
import math
from datetime import datetime
from typing import List, Dict, Any, Tuple

class MarginOptimizer:
    """
    Price optimization engine using:
    - Price elasticity calculation
    - Demand curve modeling
    - Bundle recommendations
    - Competitive positioning
    """
    
    def __init__(self):
        self.min_margin = 0.10  # Minimum 10% margin
        self.max_price_change = 0.20  # Max 20% price change
    
    def optimize_pricing(self,
                        item: Dict[str, Any],
                        sales_history: List[Dict],
                        competitor_prices: Dict[str, float] = None,
                        inventory_status: str = 'normal') -> Dict[str, Any]:
        """
        Calculate optimal pricing for an item
        
        Args:
            item: Item details (current price, cost, etc.)
            sales_history: Historical sales with prices
            competitor_prices: Competitor pricing data
            inventory_status: 'overstocked', 'normal', 'understocked'
        
        Returns:
            Optimal price with reasoning and impact simulation
        """
        item_id = item.get('itemId', '')
        item_name = item.get('name', 'Unknown')
        current_price = item.get('sellingPrice', 0)
        cost_price = item.get('costPrice', 0)
        category = item.get('category', 'groceries')
        
        # Calculate price elasticity
        elasticity = self._calculate_price_elasticity(sales_history, item_id)
        
        # Calculate optimal price
        optimal_price = self._calculate_optimal_price(
            current_price,
            cost_price,
            elasticity,
            inventory_status
        )
        
        # Simulate impact
        impact = self._simulate_price_impact(
            current_price,
            optimal_price,
            cost_price,
            elasticity,
            sales_history,
            item_id
        )
        
        # Check competitor positioning
        competitive_analysis = self._analyze_competitive_position(
            optimal_price,
            competitor_prices or {}
        )
        
        # Generate recommendation
        recommendation = self._generate_pricing_recommendation(
            item_name,
            current_price,
            optimal_price,
            elasticity,
            impact,
            inventory_status
        )
        
        return {
            'itemId': item_id,
            'itemName': item_name,
            'category': category,
            'currentPrice': round(current_price, 2),
            'costPrice': round(cost_price, 2),
            'optimalPrice': round(optimal_price, 2),
            'priceChange': round(optimal_price - current_price, 2),
            'priceChangePercent': round((optimal_price - current_price) / current_price * 100, 1) if current_price > 0 else 0,
            'elasticity': round(elasticity, 2),
            'elasticityType': self._classify_elasticity(elasticity),
            'impact': impact,
            'competitiveAnalysis': competitive_analysis,
            'recommendation': recommendation,
            'confidence': self._calculate_confidence(sales_history),
            'generatedAt': datetime.now().isoformat()
        }
    
    def recommend_bundles(self,
                         items: List[Dict],
                         sales_history: List[Dict],
                         max_bundles: int = 5) -> List[Dict]:
        """
        Recommend product bundles to increase basket size
        
        Args:
            items: List of items
            sales_history: Historical sales
            max_bundles: Maximum bundles to recommend
        
        Returns:
            List of bundle recommendations
        """
        # Find frequently bought together items
        co_occurrence = self._calculate_co_occurrence(sales_history)
        
        # Generate bundle recommendations
        bundles = []
        for (item1_id, item2_id), frequency in sorted(co_occurrence.items(), 
                                                       key=lambda x: x[1], 
                                                       reverse=True)[:max_bundles]:
            item1 = next((i for i in items if i.get('itemId') == item1_id), None)
            item2 = next((i for i in items if i.get('itemId') == item2_id), None)
            
            if item1 and item2:
                # Calculate bundle pricing
                individual_total = item1.get('sellingPrice', 0) + item2.get('sellingPrice', 0)
                bundle_discount = 0.10  # 10% discount
                bundle_price = individual_total * (1 - bundle_discount)
                
                # Calculate margin
                bundle_cost = item1.get('costPrice', 0) + item2.get('costPrice', 0)
                bundle_margin = ((bundle_price - bundle_cost) / bundle_price * 100) if bundle_price > 0 else 0
                
                bundles.append({
                    'bundleId': f"{item1_id}_{item2_id}",
                    'items': [
                        {'itemId': item1_id, 'name': item1.get('name')},
                        {'itemId': item2_id, 'name': item2.get('name')}
                    ],
                    'individualTotal': round(individual_total, 2),
                    'bundlePrice': round(bundle_price, 2),
                    'discount': round(individual_total - bundle_price, 2),
                    'discountPercent': round(bundle_discount * 100, 1),
                    'bundleMargin': round(bundle_margin, 1),
                    'frequency': frequency,
                    'recommendation': f"Customers often buy {item1.get('name')} with {item2.get('name')}"
                })
        
        return bundles
    
    def optimize_clearance(self,
                          item: Dict[str, Any],
                          days_to_expiry: int,
                          current_stock: int) -> Dict[str, Any]:
        """
        Optimize clearance strategy for dead stock or expiring items
        
        Args:
            item: Item details
            days_to_expiry: Days until expiry
            current_stock: Current stock quantity
        
        Returns:
            Clearance strategy with discount recommendations
        """
        item_name = item.get('name', 'Unknown')
        current_price = item.get('sellingPrice', 0)
        cost_price = item.get('costPrice', 0)
        
        # Calculate urgency
        if days_to_expiry <= 3:
            urgency = 'CRITICAL'
            discount_range = (0.30, 0.50)  # 30-50% off
        elif days_to_expiry <= 7:
            urgency = 'HIGH'
            discount_range = (0.20, 0.35)  # 20-35% off
        elif days_to_expiry <= 14:
            urgency = 'MEDIUM'
            discount_range = (0.10, 0.25)  # 10-25% off
        else:
            urgency = 'LOW'
            discount_range = (0.05, 0.15)  # 5-15% off
        
        # Calculate optimal discount
        optimal_discount = (discount_range[0] + discount_range[1]) / 2
        clearance_price = current_price * (1 - optimal_discount)
        
        # Ensure above cost
        if clearance_price < cost_price:
            clearance_price = cost_price * 1.05  # 5% above cost minimum
            optimal_discount = (current_price - clearance_price) / current_price
        
        # Calculate impact
        potential_loss = (current_price - clearance_price) * current_stock
        total_loss_if_expired = current_price * current_stock
        loss_avoided = total_loss_if_expired - potential_loss
        
        # Strategy recommendation
        strategies = []
        
        if urgency in ['CRITICAL', 'HIGH']:
            strategies.append('Aggressive discount')
            strategies.append('Bundle with popular items')
            strategies.append('Offer to regular customers')
        
        if current_stock > 20:
            strategies.append('Bulk discount for large purchases')
        
        strategies.append('Promote on udhaar to increase sales')
        
        return {
            'itemName': item_name,
            'urgency': urgency,
            'daysToExpiry': days_to_expiry,
            'currentStock': current_stock,
            'currentPrice': round(current_price, 2),
            'recommendedPrice': round(clearance_price, 2),
            'discount': round(optimal_discount * 100, 1),
            'priceReduction': round(current_price - clearance_price, 2),
            'impact': {
                'potentialLoss': round(potential_loss, 2),
                'totalLossIfExpired': round(total_loss_if_expired, 2),
                'lossAvoided': round(loss_avoided, 2),
                'lossAvoidedPercent': round(loss_avoided / total_loss_if_expired * 100, 1) if total_loss_if_expired > 0 else 0
            },
            'strategies': strategies,
            'recommendation': f"Apply {optimal_discount*100:.0f}% discount immediately. Potential to save ₹{loss_avoided:.0f}."
        }
    
    def _calculate_price_elasticity(self, sales_history: List[Dict], item_id: str) -> float:
        """
        Calculate price elasticity of demand
        Elasticity = % change in quantity / % change in price
        """
        # Extract price-quantity pairs for this item
        price_qty_pairs = []
        for sale in sales_history:
            for item in sale.get('items', []):
                if item.get('itemId') == item_id:
                    price = item.get('price', 0)
                    qty = item.get('quantity', 0)
                    if price > 0 and qty > 0:
                        price_qty_pairs.append((price, qty))
        
        if len(price_qty_pairs) < 5:
            # Not enough data, use category defaults
            return -1.2  # Slightly elastic (typical for groceries)
        
        # Calculate elasticity using simple regression
        prices = [p for p, q in price_qty_pairs]
        quantities = [q for p, q in price_qty_pairs]
        
        avg_price = sum(prices) / len(prices)
        avg_qty = sum(quantities) / len(quantities)
        
        # Calculate covariance and variance
        covariance = sum((p - avg_price) * (q - avg_qty) for p, q in price_qty_pairs) / len(price_qty_pairs)
        price_variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
        
        if price_variance == 0:
            return -1.2
        
        # Slope of demand curve
        slope = covariance / price_variance
        
        # Elasticity at average point
        elasticity = slope * (avg_price / avg_qty) if avg_qty > 0 else -1.2
        
        # Ensure negative (law of demand)
        elasticity = min(elasticity, -0.1)
        
        # Cap at reasonable range
        return max(-5.0, min(-0.1, elasticity))
    
    def _calculate_optimal_price(self,
                                current_price: float,
                                cost_price: float,
                                elasticity: float,
                                inventory_status: str) -> float:
        """Calculate optimal price using elasticity"""
        # Base optimal price (profit maximization)
        # P* = C * E / (E + 1) where E is elasticity
        if elasticity >= -1:
            # Inelastic demand - can increase price
            optimal_price = current_price * 1.10
        else:
            # Elastic demand - careful with price increases
            optimal_price = cost_price * abs(elasticity) / (abs(elasticity) - 1)
        
        # Adjust for inventory status
        if inventory_status == 'overstocked':
            optimal_price *= 0.95  # 5% discount to move stock
        elif inventory_status == 'understocked':
            optimal_price *= 1.05  # 5% premium for scarcity
        
        # Ensure minimum margin
        min_price = cost_price * (1 + self.min_margin)
        optimal_price = max(optimal_price, min_price)
        
        # Cap price change
        max_increase = current_price * (1 + self.max_price_change)
        max_decrease = current_price * (1 - self.max_price_change)
        optimal_price = max(max_decrease, min(max_increase, optimal_price))
        
        return optimal_price
    
    def _simulate_price_impact(self,
                              current_price: float,
                              optimal_price: float,
                              cost_price: float,
                              elasticity: float,
                              sales_history: List[Dict],
                              item_id: str) -> Dict[str, Any]:
        """Simulate impact of price change"""
        # Calculate current metrics
        current_qty = self._get_avg_quantity(sales_history, item_id)
        current_revenue = current_price * current_qty
        current_profit = (current_price - cost_price) * current_qty
        current_margin = ((current_price - cost_price) / current_price * 100) if current_price > 0 else 0
        
        # Predict new quantity using elasticity
        price_change_pct = (optimal_price - current_price) / current_price if current_price > 0 else 0
        qty_change_pct = elasticity * price_change_pct
        new_qty = current_qty * (1 + qty_change_pct)
        
        # Calculate new metrics
        new_revenue = optimal_price * new_qty
        new_profit = (optimal_price - cost_price) * new_qty
        new_margin = ((optimal_price - cost_price) / optimal_price * 100) if optimal_price > 0 else 0
        
        # Calculate changes
        revenue_change = new_revenue - current_revenue
        profit_change = new_profit - current_profit
        
        return {
            'current': {
                'avgQuantity': round(current_qty, 1),
                'revenue': round(current_revenue, 2),
                'profit': round(current_profit, 2),
                'margin': round(current_margin, 1)
            },
            'projected': {
                'avgQuantity': round(new_qty, 1),
                'revenue': round(new_revenue, 2),
                'profit': round(new_profit, 2),
                'margin': round(new_margin, 1)
            },
            'changes': {
                'quantityChange': round(new_qty - current_qty, 1),
                'quantityChangePercent': round(qty_change_pct * 100, 1),
                'revenueChange': round(revenue_change, 2),
                'revenueChangePercent': round(revenue_change / current_revenue * 100, 1) if current_revenue > 0 else 0,
                'profitChange': round(profit_change, 2),
                'profitChangePercent': round(profit_change / current_profit * 100, 1) if current_profit > 0 else 0
            }
        }
    
    def _analyze_competitive_position(self,
                                     optimal_price: float,
                                     competitor_prices: Dict[str, float]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        if not competitor_prices:
            return {'status': 'NO_DATA', 'message': 'No competitor data available'}
        
        competitor_avg = sum(competitor_prices.values()) / len(competitor_prices)
        min_competitor = min(competitor_prices.values())
        max_competitor = max(competitor_prices.values())
        
        # Determine position
        if optimal_price < min_competitor:
            position = 'PRICE_LEADER'
            message = 'Lowest price in market'
        elif optimal_price <= competitor_avg:
            position = 'COMPETITIVE'
            message = 'Competitively priced'
        elif optimal_price <= max_competitor:
            position = 'PREMIUM'
            message = 'Premium pricing'
        else:
            position = 'OVERPRICED'
            message = 'Above market rates'
        
        return {
            'position': position,
            'message': message,
            'optimalPrice': round(optimal_price, 2),
            'competitorAvg': round(competitor_avg, 2),
            'competitorMin': round(min_competitor, 2),
            'competitorMax': round(max_competitor, 2),
            'priceVsAvg': round(optimal_price - competitor_avg, 2),
            'priceVsAvgPercent': round((optimal_price - competitor_avg) / competitor_avg * 100, 1) if competitor_avg > 0 else 0
        }
    
    def _generate_pricing_recommendation(self,
                                        item_name: str,
                                        current_price: float,
                                        optimal_price: float,
                                        elasticity: float,
                                        impact: Dict,
                                        inventory_status: str) -> str:
        """Generate human-readable recommendation"""
        price_change = optimal_price - current_price
        price_change_pct = (price_change / current_price * 100) if current_price > 0 else 0
        
        if abs(price_change) < 0.50:
            return f"✓ {item_name} is optimally priced. No change needed."
        
        if price_change > 0:
            action = "Increase"
            direction = "up"
        else:
            action = "Decrease"
            direction = "down"
        
        profit_change = impact['changes']['profitChange']
        
        recommendation = f"{action} {item_name} price by ₹{abs(price_change):.2f} ({abs(price_change_pct):.1f}% {direction}). "
        
        if profit_change > 0:
            recommendation += f"Expected profit increase: ₹{profit_change:.2f}. "
        else:
            recommendation += f"Trade-off: Lower margin but higher volume. "
        
        if inventory_status == 'overstocked':
            recommendation += "Helps clear excess stock."
        elif inventory_status == 'understocked':
            recommendation += "Maximizes profit during scarcity."
        
        elasticity_type = self._classify_elasticity(elasticity)
        if elasticity_type == 'INELASTIC':
            recommendation += " Demand is inelastic - price increase won't hurt sales much."
        elif elasticity_type == 'ELASTIC':
            recommendation += " Demand is elastic - price changes will significantly affect sales."
        
        return recommendation
    
    def _classify_elasticity(self, elasticity: float) -> str:
        """Classify elasticity type"""
        abs_e = abs(elasticity)
        if abs_e < 1:
            return 'INELASTIC'
        elif abs_e > 2:
            return 'HIGHLY_ELASTIC'
        else:
            return 'ELASTIC'
    
    def _get_avg_quantity(self, sales_history: List[Dict], item_id: str) -> float:
        """Get average quantity sold"""
        quantities = []
        for sale in sales_history:
            for item in sale.get('items', []):
                if item.get('itemId') == item_id:
                    quantities.append(item.get('quantity', 0))
        
        return sum(quantities) / len(quantities) if quantities else 5.0
    
    def _calculate_co_occurrence(self, sales_history: List[Dict]) -> Dict[Tuple[str, str], int]:
        """Calculate item co-occurrence in transactions"""
        co_occurrence = {}
        
        for sale in sales_history:
            items = sale.get('items', [])
            item_ids = [item.get('itemId') for item in items]
            
            # Count pairs
            for i in range(len(item_ids)):
                for j in range(i + 1, len(item_ids)):
                    pair = tuple(sorted([item_ids[i], item_ids[j]]))
                    co_occurrence[pair] = co_occurrence.get(pair, 0) + 1
        
        return co_occurrence
    
    def _calculate_confidence(self, sales_history: List[Dict]) -> float:
        """Calculate confidence in recommendation"""
        data_points = len(sales_history)
        
        if data_points >= 50:
            return 0.95
        elif data_points >= 30:
            return 0.85
        elif data_points >= 15:
            return 0.70
        elif data_points >= 5:
            return 0.55
        else:
            return 0.40


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'optimize')
        
        optimizer = MarginOptimizer()
        
        if action == 'optimize':
            item = body.get('item', {})
            sales_history = body.get('salesHistory', [])
            competitor_prices = body.get('competitorPrices')
            inventory_status = body.get('inventoryStatus', 'normal')
            
            result = optimizer.optimize_pricing(
                item,
                sales_history,
                competitor_prices,
                inventory_status
            )
        
        elif action == 'bundles':
            items = body.get('items', [])
            sales_history = body.get('salesHistory', [])
            max_bundles = body.get('maxBundles', 5)
            
            result = {'bundles': optimizer.recommend_bundles(items, sales_history, max_bundles)}
        
        elif action == 'clearance':
            item = body.get('item', {})
            days_to_expiry = body.get('daysToExpiry', 7)
            current_stock = body.get('currentStock', 0)
            
            result = optimizer.optimize_clearance(item, days_to_expiry, current_stock)
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid action'})
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
