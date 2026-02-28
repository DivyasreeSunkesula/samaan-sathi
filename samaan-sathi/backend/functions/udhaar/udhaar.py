import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle udhaar (credit) management operations
    """
    try:
        method = event.get('httpMethod')
        path = event.get('path', '')
        shop_id = get_shop_id(event)
        
        if not shop_id:
            return response(401, {'error': 'Unauthorized'})
        
        if method == 'GET':
            if '{customerId}' in path:
                customer_id = event['pathParameters']['customerId']
                return get_customer_udhaar(shop_id, customer_id)
            else:
                return get_all_udhaar(shop_id, event.get('queryStringParameters', {}))
        
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            if '/payment' in path:
                return record_payment(shop_id, body)
            else:
                return add_udhaar(shop_id, body)
        
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Udhaar Error: {str(e)}")
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('custom:shopId', 'default-shop')
    except:
        return None


def get_all_udhaar(shop_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get all udhaar records for shop"""
    try:
        # Get udhaar table from environment
        table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        table = dynamodb.Table(table_name)
        
        result = table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id}
        )
        
        records = result.get('Items', [])
        
        # Calculate summary statistics
        total_outstanding = sum(float(r.get('outstandingAmount', 0)) for r in records)
        overdue_count = sum(1 for r in records if is_overdue(r))
        
        # Filter by status if provided
        status = params.get('status')
        if status:
            records = [r for r in records if r.get('status') == status]
        
        return response(200, {
            'shopId': shop_id,
            'records': records,
            'summary': {
                'totalOutstanding': round(total_outstanding, 2),
                'totalCustomers': len(records),
                'overdueCount': overdue_count
            }
        })
        
    except Exception as e:
        print(f"Get udhaar error: {str(e)}")
        return response(500, {'error': 'Failed to fetch udhaar records'})


def get_customer_udhaar(shop_id: str, customer_id: str) -> Dict[str, Any]:
    """Get udhaar record for specific customer"""
    try:
        table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        table = dynamodb.Table(table_name)
        
        result = table.get_item(
            Key={'shopId': shop_id, 'customerId': customer_id}
        )
        
        if 'Item' not in result:
            return response(404, {'error': 'Customer not found'})
        
        record = result['Item']
        
        # Get transaction history
        transactions = record.get('transactions', [])
        
        return response(200, {
            'customer': record,
            'transactions': transactions,
            'riskScore': calculate_risk_score(record)
        })
        
    except Exception as e:
        print(f"Get customer udhaar error: {str(e)}")
        return response(500, {'error': 'Failed to fetch customer record'})


def add_udhaar(shop_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Add new udhaar entry"""
    try:
        customer_id = body.get('customerId')
        customer_name = body.get('customerName')
        amount = Decimal(str(body.get('amount', 0)))
        items = body.get('items', [])
        
        if not customer_id or amount <= 0:
            return response(400, {'error': 'customerId and positive amount required'})
        
        table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        table = dynamodb.Table(table_name)
        
        # Get existing record or create new
        result = table.get_item(
            Key={'shopId': shop_id, 'customerId': customer_id}
        )
        
        if 'Item' in result:
            record = result['Item']
            outstanding = Decimal(str(record.get('outstandingAmount', 0)))
            transactions = record.get('transactions', [])
        else:
            outstanding = Decimal('0')
            transactions = []
        
        # Add new transaction
        transaction = {
            'transactionId': f"txn-{datetime.utcnow().timestamp()}",
            'type': 'CREDIT',
            'amount': float(amount),
            'items': items,
            'date': datetime.utcnow().isoformat(),
            'dueDate': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        transactions.append(transaction)
        outstanding += amount
        
        # Update record
        updated_record = {
            'shopId': shop_id,
            'customerId': customer_id,
            'customerName': customer_name,
            'outstandingAmount': outstanding,
            'transactions': transactions,
            'lastUpdated': datetime.utcnow().isoformat(),
            'status': 'PENDING' if outstanding > 0 else 'PAID',
            'dueDate': transaction['dueDate']
        }
        
        table.put_item(Item=updated_record)
        
        return response(200, {
            'message': 'Udhaar added successfully',
            'record': updated_record
        })
        
    except Exception as e:
        print(f"Add udhaar error: {str(e)}")
        return response(500, {'error': 'Failed to add udhaar'})


def record_payment(shop_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Record udhaar payment"""
    try:
        customer_id = body.get('customerId')
        amount = Decimal(str(body.get('amount', 0)))
        
        if not customer_id or amount <= 0:
            return response(400, {'error': 'customerId and positive amount required'})
        
        table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        table = dynamodb.Table(table_name)
        
        # Get existing record
        result = table.get_item(
            Key={'shopId': shop_id, 'customerId': customer_id}
        )
        
        if 'Item' not in result:
            return response(404, {'error': 'Customer not found'})
        
        record = result['Item']
        outstanding = Decimal(str(record.get('outstandingAmount', 0)))
        transactions = record.get('transactions', [])
        
        if amount > outstanding:
            return response(400, {'error': 'Payment amount exceeds outstanding balance'})
        
        # Add payment transaction
        transaction = {
            'transactionId': f"txn-{datetime.utcnow().timestamp()}",
            'type': 'PAYMENT',
            'amount': float(amount),
            'date': datetime.utcnow().isoformat()
        }
        
        transactions.append(transaction)
        outstanding -= amount
        
        # Update record
        record['outstandingAmount'] = outstanding
        record['transactions'] = transactions
        record['lastUpdated'] = datetime.utcnow().isoformat()
        record['status'] = 'PAID' if outstanding == 0 else 'PENDING'
        
        table.put_item(Item=record)
        
        return response(200, {
            'message': 'Payment recorded successfully',
            'record': record
        })
        
    except Exception as e:
        print(f"Record payment error: {str(e)}")
        return response(500, {'error': 'Failed to record payment'})


def is_overdue(record: Dict[str, Any]) -> bool:
    """Check if udhaar is overdue"""
    try:
        due_date_str = record.get('dueDate')
        if not due_date_str:
            return False
        
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return datetime.utcnow() > due_date and float(record.get('outstandingAmount', 0)) > 0
    except:
        return False


def calculate_risk_score(record: Dict[str, Any]) -> float:
    """Calculate customer risk score (0-1, higher is riskier)"""
    try:
        outstanding = float(record.get('outstandingAmount', 0))
        transactions = record.get('transactions', [])
        
        if not transactions:
            return 0.5
        
        # Factors: outstanding amount, overdue status, payment history
        risk = 0.0
        
        # Outstanding amount factor
        if outstanding > 10000:
            risk += 0.4
        elif outstanding > 5000:
            risk += 0.2
        
        # Overdue factor
        if is_overdue(record):
            risk += 0.3
        
        # Payment history factor
        payments = [t for t in transactions if t['type'] == 'PAYMENT']
        credits = [t for t in transactions if t['type'] == 'CREDIT']
        
        if len(credits) > 0:
            payment_ratio = len(payments) / len(credits)
            if payment_ratio < 0.5:
                risk += 0.3
        
        return min(1.0, risk)
        
    except Exception as e:
        print(f"Risk calculation error: {str(e)}")
        return 0.5


def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }
