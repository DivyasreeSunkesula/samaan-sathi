import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Generate and retrieve alerts for shop owners
    """
    try:
        shop_id = get_shop_id(event)
        
        if not shop_id:
            return response(401, {'error': 'Unauthorized'})
        
        # Generate alerts based on current data
        alerts = generate_alerts(shop_id)
        
        return response(200, {
            'shopId': shop_id,
            'alerts': alerts,
            'count': len(alerts),
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Alerts Error: {str(e)}")
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('custom:shopId', 'default-shop')
    except:
        return None


def generate_alerts(shop_id: str) -> List[Dict[str, Any]]:
    """Generate all types of alerts"""
    alerts = []
    
    # Inventory alerts
    alerts.extend(check_inventory_alerts(shop_id))
    
    # Udhaar alerts
    alerts.extend(check_udhaar_alerts(shop_id))
    
    # Expiry alerts
    alerts.extend(check_expiry_alerts(shop_id))
    
    # Sort by priority
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    alerts.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 3))
    
    return alerts


def check_inventory_alerts(shop_id: str) -> List[Dict[str, Any]]:
    """Check for inventory-related alerts"""
    alerts = []
    
    try:
        table = dynamodb.Table(os.environ['INVENTORY_TABLE'])
        result = table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id}
        )
        
        items = result.get('Items', [])
        
        # Low stock alerts
        low_stock_items = []
        out_of_stock_items = []
        
        for item in items:
            quantity = float(item.get('quantity', 0))
            min_level = float(item.get('minStockLevel', 0))
            
            if quantity == 0:
                out_of_stock_items.append(item.get('name', 'Unknown'))
            elif quantity < min_level:
                low_stock_items.append(item.get('name', 'Unknown'))
        
        if out_of_stock_items:
            alerts.append({
                'type': 'OUT_OF_STOCK',
                'priority': 'CRITICAL',
                'title': 'Items Out of Stock',
                'message': f"{len(out_of_stock_items)} items are out of stock: {', '.join(out_of_stock_items[:3])}",
                'action': 'Restock immediately to avoid lost sales',
                'items': out_of_stock_items
            })
        
        if low_stock_items:
            alerts.append({
                'type': 'LOW_STOCK',
                'priority': 'HIGH',
                'title': 'Low Stock Warning',
                'message': f"{len(low_stock_items)} items are running low: {', '.join(low_stock_items[:3])}",
                'action': 'Plan restocking for these items',
                'items': low_stock_items
            })
        
    except Exception as e:
        print(f"Inventory alerts error: {str(e)}")
    
    return alerts


def check_udhaar_alerts(shop_id: str) -> List[Dict[str, Any]]:
    """Check for udhaar-related alerts"""
    alerts = []
    
    try:
        table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        table = dynamodb.Table(table_name)
        
        result = table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id}
        )
        
        records = result.get('Items', [])
        
        # Calculate overdue and high-risk customers
        overdue_customers = []
        high_risk_customers = []
        total_overdue_amount = 0
        
        for record in records:
            outstanding = float(record.get('outstandingAmount', 0))
            
            if outstanding > 0:
                due_date_str = record.get('dueDate')
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        if datetime.utcnow() > due_date:
                            overdue_customers.append({
                                'name': record.get('customerName', 'Unknown'),
                                'amount': outstanding
                            })
                            total_overdue_amount += outstanding
                    except:
                        pass
                
                # High outstanding amount
                if outstanding > 5000:
                    high_risk_customers.append({
                        'name': record.get('customerName', 'Unknown'),
                        'amount': outstanding
                    })
        
        if overdue_customers:
            alerts.append({
                'type': 'OVERDUE_UDHAAR',
                'priority': 'HIGH',
                'title': 'Overdue Payments',
                'message': f"₹{round(total_overdue_amount, 2)} overdue from {len(overdue_customers)} customers",
                'action': 'Follow up with customers for payment',
                'customers': overdue_customers[:5]
            })
        
        if high_risk_customers:
            alerts.append({
                'type': 'HIGH_UDHAAR',
                'priority': 'MEDIUM',
                'title': 'High Outstanding Credit',
                'message': f"{len(high_risk_customers)} customers have high outstanding amounts",
                'action': 'Consider limiting further credit',
                'customers': high_risk_customers[:5]
            })
        
    except Exception as e:
        print(f"Udhaar alerts error: {str(e)}")
    
    return alerts


def check_expiry_alerts(shop_id: str) -> List[Dict[str, Any]]:
    """Check for expiry-related alerts"""
    alerts = []
    
    try:
        table = dynamodb.Table(os.environ['INVENTORY_TABLE'])
        result = table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id}
        )
        
        items = result.get('Items', [])
        
        expiring_soon = []
        expired = []
        
        today = datetime.utcnow().date()
        warning_date = today + timedelta(days=7)
        
        for item in items:
            expiry_str = item.get('expiryDate')
            if expiry_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_str).date()
                    
                    if expiry_date < today:
                        expired.append(item.get('name', 'Unknown'))
                    elif expiry_date <= warning_date:
                        expiring_soon.append({
                            'name': item.get('name', 'Unknown'),
                            'expiryDate': expiry_str,
                            'quantity': float(item.get('quantity', 0))
                        })
                except:
                    pass
        
        if expired:
            alerts.append({
                'type': 'EXPIRED',
                'priority': 'CRITICAL',
                'title': 'Expired Items',
                'message': f"{len(expired)} items have expired: {', '.join(expired[:3])}",
                'action': 'Remove from inventory immediately',
                'items': expired
            })
        
        if expiring_soon:
            alerts.append({
                'type': 'EXPIRING_SOON',
                'priority': 'MEDIUM',
                'title': 'Items Expiring Soon',
                'message': f"{len(expiring_soon)} items expiring within 7 days",
                'action': 'Consider discount or promotion to clear stock',
                'items': expiring_soon[:5]
            })
        
    except Exception as e:
        print(f"Expiry alerts error: {str(e)}")
    
    return alerts


def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(body)
    }
