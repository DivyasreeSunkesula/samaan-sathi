"""
Credit Risk Scoring & Customer Clustering Engine
ML-based customer segmentation and dynamic credit limit calculation
"""
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

class CreditRiskScorer:
    """
    Customer credit risk assessment using:
    - Payment history analysis
    - Behavioral clustering
    - Risk scoring
    - Dynamic credit limit calculation
    """
    
    # Risk categories and their characteristics
    RISK_CATEGORIES = {
        'RELIABLE_PAYER': {
            'score_range': (80, 100),
            'credit_multiplier': 1.5,
            'description': 'Always pays on time, high trust',
            'color': 'green'
        },
        'SEASONAL_BORROWER': {
            'score_range': (60, 79),
            'credit_multiplier': 1.2,
            'description': 'Pays reliably but takes time during certain seasons',
            'color': 'blue'
        },
        'MODERATE_RISK': {
            'score_range': (40, 59),
            'credit_multiplier': 0.8,
            'description': 'Occasional delays, needs monitoring',
            'color': 'yellow'
        },
        'CHRONIC_DELAYER': {
            'score_range': (20, 39),
            'credit_multiplier': 0.5,
            'description': 'Frequent delays, high risk',
            'color': 'orange'
        },
        'HIGH_RISK': {
            'score_range': (0, 19),
            'credit_multiplier': 0.2,
            'description': 'Very unreliable, cash-only recommended',
            'color': 'red'
        }
    }
    
    def __init__(self):
        self.base_credit_limit = 5000  # Base credit limit in rupees
    
    def score_customer(self, customer: Dict[str, Any], 
                      udhaar_history: List[Dict], 
                      sales_history: List[Dict]) -> Dict[str, Any]:
        """
        Calculate comprehensive credit risk score for a customer
        
        Args:
            customer: Customer details
            udhaar_history: Historical udhaar transactions
            sales_history: Historical sales to this customer
        
        Returns:
            Risk score, category, recommended credit limit, and insights
        """
        customer_id = customer.get('customerId', '')
        customer_name = customer.get('customerName', 'Unknown')
        
        # Calculate individual risk factors
        payment_score = self._calculate_payment_score(udhaar_history)
        frequency_score = self._calculate_frequency_score(sales_history)
        amount_score = self._calculate_amount_score(udhaar_history)
        recency_score = self._calculate_recency_score(udhaar_history)
        consistency_score = self._calculate_consistency_score(udhaar_history)
        
        # Weighted composite score
        weights = {
            'payment': 0.40,      # Most important
            'frequency': 0.20,
            'amount': 0.15,
            'recency': 0.15,
            'consistency': 0.10
        }
        
        composite_score = (
            payment_score * weights['payment'] +
            frequency_score * weights['frequency'] +
            amount_score * weights['amount'] +
            recency_score * weights['recency'] +
            consistency_score * weights['consistency']
        )
        
        # Determine risk category
        risk_category = self._determine_risk_category(composite_score)
        category_info = self.RISK_CATEGORIES[risk_category]
        
        # Calculate recommended credit limit
        credit_limit = self._calculate_credit_limit(
            composite_score, 
            udhaar_history, 
            sales_history,
            category_info['credit_multiplier']
        )
        
        # Calculate current exposure
        current_outstanding = sum(
            u.get('amount', 0) - u.get('paidAmount', 0) 
            for u in udhaar_history 
            if u.get('status') != 'PAID'
        )
        
        # Calculate utilization
        utilization = (current_outstanding / credit_limit * 100) if credit_limit > 0 else 0
        
        # Generate insights
        insights = self._generate_insights(
            customer_name,
            composite_score,
            risk_category,
            payment_score,
            current_outstanding,
            credit_limit,
            utilization,
            udhaar_history
        )
        
        # Calculate payment behavior metrics
        avg_payment_delay = self._calculate_avg_payment_delay(udhaar_history)
        payment_reliability = payment_score / 100
        
        return {
            'customerId': customer_id,
            'customerName': customer_name,
            'riskScore': round(composite_score, 1),
            'riskCategory': risk_category,
            'riskLevel': category_info['description'],
            'riskColor': category_info['color'],
            'recommendedCreditLimit': round(credit_limit, 0),
            'currentOutstanding': round(current_outstanding, 2),
            'creditUtilization': round(utilization, 1),
            'availableCredit': round(max(0, credit_limit - current_outstanding), 2),
            'scoreBreakdown': {
                'paymentScore': round(payment_score, 1),
                'frequencyScore': round(frequency_score, 1),
                'amountScore': round(amount_score, 1),
                'recencyScore': round(recency_score, 1),
                'consistencyScore': round(consistency_score, 1)
            },
            'behaviorMetrics': {
                'avgPaymentDelay': round(avg_payment_delay, 1),
                'paymentReliability': round(payment_reliability, 2),
                'totalTransactions': len(udhaar_history),
                'paidTransactions': len([u for u in udhaar_history if u.get('status') == 'PAID']),
                'overdueTransactions': len([u for u in udhaar_history if u.get('status') == 'OVERDUE'])
            },
            'insights': insights,
            'lastUpdated': datetime.now().isoformat()
        }
    
    def cluster_customers(self, customers_data: List[Dict]) -> Dict[str, Any]:
        """
        Cluster all customers into risk categories
        
        Args:
            customers_data: List of customer risk scores
        
        Returns:
            Clustering analysis and distribution
        """
        if not customers_data:
            return {'error': 'No customer data provided'}
        
        # Group by risk category
        clusters = {}
        for category in self.RISK_CATEGORIES.keys():
            clusters[category] = []
        
        for customer in customers_data:
            category = customer.get('riskCategory', 'MODERATE_RISK')
            clusters[category].append(customer)
        
        # Calculate statistics
        total_customers = len(customers_data)
        total_outstanding = sum(c.get('currentOutstanding', 0) for c in customers_data)
        total_credit_limit = sum(c.get('recommendedCreditLimit', 0) for c in customers_data)
        
        # Distribution analysis
        distribution = {}
        for category, customers in clusters.items():
            count = len(customers)
            percentage = (count / total_customers * 100) if total_customers > 0 else 0
            outstanding = sum(c.get('currentOutstanding', 0) for c in customers)
            
            distribution[category] = {
                'count': count,
                'percentage': round(percentage, 1),
                'totalOutstanding': round(outstanding, 2),
                'avgScore': round(sum(c.get('riskScore', 0) for c in customers) / count, 1) if count > 0 else 0
            }
        
        # Identify high-risk customers
        high_risk_customers = [
            c for c in customers_data 
            if c.get('riskCategory') in ['CHRONIC_DELAYER', 'HIGH_RISK']
        ]
        
        # Calculate portfolio risk
        portfolio_risk_score = self._calculate_portfolio_risk(customers_data)
        
        return {
            'totalCustomers': total_customers,
            'totalOutstanding': round(total_outstanding, 2),
            'totalCreditLimit': round(total_credit_limit, 2),
            'overallUtilization': round((total_outstanding / total_credit_limit * 100) if total_credit_limit > 0 else 0, 1),
            'portfolioRiskScore': round(portfolio_risk_score, 1),
            'distribution': distribution,
            'highRiskCount': len(high_risk_customers),
            'highRiskOutstanding': round(sum(c.get('currentOutstanding', 0) for c in high_risk_customers), 2),
            'recommendations': self._generate_portfolio_recommendations(
                distribution, 
                portfolio_risk_score,
                total_outstanding,
                high_risk_customers
            ),
            'generatedAt': datetime.now().isoformat()
        }
    
    def _calculate_payment_score(self, udhaar_history: List[Dict]) -> float:
        """Score based on payment history (0-100)"""
        if not udhaar_history:
            return 50.0  # Neutral for new customers
        
        paid_count = len([u for u in udhaar_history if u.get('status') == 'PAID'])
        overdue_count = len([u for u in udhaar_history if u.get('status') == 'OVERDUE'])
        total_count = len(udhaar_history)
        
        # Payment rate
        payment_rate = paid_count / total_count if total_count > 0 else 0.5
        
        # Penalty for overdue
        overdue_penalty = overdue_count * 10
        
        score = (payment_rate * 100) - overdue_penalty
        return max(0, min(100, score))
    
    def _calculate_frequency_score(self, sales_history: List[Dict]) -> float:
        """Score based on purchase frequency (0-100)"""
        if not sales_history:
            return 50.0
        
        # More frequent purchases = higher score (loyal customer)
        frequency = len(sales_history)
        
        if frequency >= 50:
            return 100.0
        elif frequency >= 30:
            return 85.0
        elif frequency >= 15:
            return 70.0
        elif frequency >= 5:
            return 55.0
        else:
            return 40.0
    
    def _calculate_amount_score(self, udhaar_history: List[Dict]) -> float:
        """Score based on transaction amounts (0-100)"""
        if not udhaar_history:
            return 50.0
        
        amounts = [u.get('amount', 0) for u in udhaar_history]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        
        # Moderate amounts are better (not too small, not too large)
        if 500 <= avg_amount <= 3000:
            return 90.0
        elif 200 <= avg_amount < 500 or 3000 < avg_amount <= 5000:
            return 75.0
        elif avg_amount < 200 or avg_amount > 5000:
            return 60.0
        else:
            return 50.0
    
    def _calculate_recency_score(self, udhaar_history: List[Dict]) -> float:
        """Score based on recent activity (0-100)"""
        if not udhaar_history:
            return 50.0
        
        # Check last transaction date
        try:
            last_transaction = max(
                datetime.fromisoformat(u.get('createdAt', '2020-01-01'))
                for u in udhaar_history
            )
            days_since = (datetime.now() - last_transaction).days
            
            if days_since <= 7:
                return 100.0
            elif days_since <= 30:
                return 85.0
            elif days_since <= 90:
                return 70.0
            elif days_since <= 180:
                return 55.0
            else:
                return 40.0
        except:
            return 50.0
    
    def _calculate_consistency_score(self, udhaar_history: List[Dict]) -> float:
        """Score based on payment consistency (0-100)"""
        if len(udhaar_history) < 3:
            return 50.0
        
        # Calculate variance in payment delays
        delays = []
        for u in udhaar_history:
            if u.get('status') == 'PAID':
                try:
                    created = datetime.fromisoformat(u.get('createdAt', ''))
                    paid = datetime.fromisoformat(u.get('paidAt', ''))
                    delay = (paid - created).days
                    delays.append(delay)
                except:
                    pass
        
        if not delays:
            return 50.0
        
        avg_delay = sum(delays) / len(delays)
        variance = sum((d - avg_delay) ** 2 for d in delays) / len(delays)
        std_dev = math.sqrt(variance)
        
        # Lower variance = higher consistency = higher score
        if std_dev <= 3:
            return 95.0
        elif std_dev <= 7:
            return 80.0
        elif std_dev <= 15:
            return 65.0
        else:
            return 50.0
    
    def _determine_risk_category(self, score: float) -> str:
        """Determine risk category based on score"""
        for category, info in self.RISK_CATEGORIES.items():
            min_score, max_score = info['score_range']
            if min_score <= score <= max_score:
                return category
        return 'MODERATE_RISK'
    
    def _calculate_credit_limit(self, score: float, udhaar_history: List[Dict], 
                               sales_history: List[Dict], multiplier: float) -> float:
        """Calculate recommended credit limit"""
        # Base limit adjusted by risk score
        base_limit = self.base_credit_limit * (score / 100)
        
        # Adjust by purchase history
        if sales_history:
            avg_purchase = sum(s.get('totalAmount', 0) for s in sales_history) / len(sales_history)
            # Credit limit should cover 2-3 typical purchases
            history_based_limit = avg_purchase * 2.5
            base_limit = (base_limit + history_based_limit) / 2
        
        # Apply category multiplier
        final_limit = base_limit * multiplier
        
        # Round to nearest 500
        return round(final_limit / 500) * 500
    
    def _calculate_avg_payment_delay(self, udhaar_history: List[Dict]) -> float:
        """Calculate average payment delay in days"""
        delays = []
        for u in udhaar_history:
            if u.get('status') == 'PAID':
                try:
                    created = datetime.fromisoformat(u.get('createdAt', ''))
                    paid = datetime.fromisoformat(u.get('paidAt', ''))
                    delay = (paid - created).days
                    delays.append(delay)
                except:
                    pass
        
        return sum(delays) / len(delays) if delays else 0
    
    def _generate_insights(self, name: str, score: float, category: str, 
                          payment_score: float, outstanding: float, 
                          limit: float, utilization: float, history: List[Dict]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Risk-based insights
        if category == 'HIGH_RISK':
            insights.append(f"⚠️ {name} is high-risk. Recommend cash-only transactions.")
        elif category == 'CHRONIC_DELAYER':
            insights.append(f"⚠️ {name} frequently delays payments. Monitor closely.")
        elif category == 'RELIABLE_PAYER':
            insights.append(f"✓ {name} is a reliable customer. Safe for higher credit.")
        
        # Utilization insights
        if utilization > 90:
            insights.append(f"⚠️ Credit utilization at {utilization:.0f}%. Limit reached.")
        elif utilization > 70:
            insights.append(f"⚠️ Credit utilization at {utilization:.0f}%. Approaching limit.")
        
        # Outstanding insights
        if outstanding > limit:
            insights.append(f"🚨 Outstanding (₹{outstanding:.0f}) exceeds limit (₹{limit:.0f})!")
        
        # Payment behavior insights
        if payment_score < 50:
            insights.append(f"⚠️ Poor payment history. Consider reducing credit limit.")
        
        return insights
    
    def _calculate_portfolio_risk(self, customers_data: List[Dict]) -> float:
        """Calculate overall portfolio risk score"""
        if not customers_data:
            return 50.0
        
        # Weighted average of all customer scores
        total_outstanding = sum(c.get('currentOutstanding', 0) for c in customers_data)
        
        if total_outstanding == 0:
            # Simple average if no outstanding
            return sum(c.get('riskScore', 50) for c in customers_data) / len(customers_data)
        
        # Weighted by outstanding amount
        weighted_score = sum(
            c.get('riskScore', 50) * c.get('currentOutstanding', 0)
            for c in customers_data
        ) / total_outstanding
        
        return weighted_score
    
    def _generate_portfolio_recommendations(self, distribution: Dict, 
                                           portfolio_risk: float,
                                           total_outstanding: float,
                                           high_risk_customers: List[Dict]) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        # Overall risk assessment
        if portfolio_risk < 60:
            recommendations.append("🚨 High portfolio risk detected. Tighten credit policies.")
        elif portfolio_risk < 75:
            recommendations.append("⚠️ Moderate portfolio risk. Monitor high-risk customers closely.")
        else:
            recommendations.append("✓ Portfolio risk is manageable.")
        
        # High-risk customer concentration
        high_risk_pct = distribution.get('HIGH_RISK', {}).get('percentage', 0)
        chronic_pct = distribution.get('CHRONIC_DELAYER', {}).get('percentage', 0)
        
        if high_risk_pct + chronic_pct > 30:
            recommendations.append(f"⚠️ {high_risk_pct + chronic_pct:.0f}% customers are high-risk. Reduce new credit.")
        
        # Outstanding concentration
        if len(high_risk_customers) > 0:
            high_risk_outstanding = sum(c.get('currentOutstanding', 0) for c in high_risk_customers)
            concentration = (high_risk_outstanding / total_outstanding * 100) if total_outstanding > 0 else 0
            
            if concentration > 40:
                recommendations.append(f"🚨 {concentration:.0f}% of outstanding is with high-risk customers!")
        
        return recommendations


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'score')
        
        scorer = CreditRiskScorer()
        
        if action == 'score':
            customer = body.get('customer', {})
            udhaar_history = body.get('udhaarHistory', [])
            sales_history = body.get('salesHistory', [])
            
            result = scorer.score_customer(customer, udhaar_history, sales_history)
        
        elif action == 'cluster':
            customers_data = body.get('customersData', [])
            result = scorer.cluster_customers(customers_data)
        
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
