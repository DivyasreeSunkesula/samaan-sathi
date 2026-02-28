import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['INVENTORY_TABLE'])

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle inventory management operations
    """
    try:
        method = event.get('httpMethod')
        path = event.get('path', '')
        shop_id = get_shop_id(event)
        
        if not shop_id:
            return response(401, {'error': 'Unauthorized'})
        
        if method == 'GET':
            if '{itemId}' in path:
                item_id = event['pathParameters']['itemId']
                return get_item(shop_id, item_id)
            else:
                return get_all_items(shop_id, event.get('queryStringParameters', {}))
        
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            return add_or_update_item(shop_id, body)
        
        elif method == 'DELETE':
            item_id = event['pathParameters']['itemId']
            return delete_item(shop_id, item_id)
        
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token"""
    try:
        # In production, decode JWT and extract shop_id
        # For now, use a header or query parameter
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('custom:shopId', 'default-shop')
    except:
        return None


def get_all_items(shop_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get all inventory items for a shop"""
    try:
        query_params = {
            'KeyConditionExpression': 'shopId = :shopId',
            'ExpressionAttributeValues': {':shopId': shop_id}
        }
        
        # Filter by category if provided
        category = params.get('category')
        if category:
            query_params['FilterExpression'] = 'category = :category'
            query_params['ExpressionAttributeValues'][':category'] = category
        
        result = table.query(**query_params)
        
        return response(200, {
            'items': result.get('Items', []),
            'count': len(result.get('Items', []))
        })
        
    except Exception as e:
        print(f"Get items error: {str(e)}")
        return response(500, {'error': 'Failed to fetch items'})


def get_item(shop_id: str, item_id: str) -> Dict[str, Any]:
    """Get specific inventory item"""
    try:
        result = table.get_item(
            Key={'shopId': shop_id, 'itemId': item_id}
        )
        
        if 'Item' not in result:
            return response(404, {'error': 'Item not found'})
        
        return response(200, result['Item'])
        
    except Exception as e:
        print(f"Get item error: {str(e)}")
        return response(500, {'error': 'Failed to fetch item'})


def add_or_update_item(shop_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Add new item or update existing item"""
    try:
        item_id = body.get('itemId')
        if not item_id:
            return response(400, {'error': 'itemId is required'})
        
        item = {
            'shopId': shop_id,
            'itemId': item_id,
            'name': body.get('name'),
            'category': body.get('category', 'general'),
            'quantity': Decimal(str(body.get('quantity', 0))),
            'unit': body.get('unit', 'pcs'),
            'costPrice': Decimal(str(body.get('costPrice', 0))),
            'sellingPrice': Decimal(str(body.get('sellingPrice', 0))),
            'minStockLevel': Decimal(str(body.get('minStockLevel', 0))),
            'expiryDate': body.get('expiryDate'),
            'supplier': body.get('supplier'),
            'lastUpdated': datetime.utcnow().isoformat(),
            'updatedBy': 'system'
        }
        
        # Remove None values
        item = {k: v for k, v in item.items() if v is not None}
        
        table.put_item(Item=item)
        
        return response(200, {
            'message': 'Item saved successfully',
            'item': item
        })
        
    except Exception as e:
        print(f"Save item error: {str(e)}")
        return response(500, {'error': 'Failed to save item'})


def delete_item(shop_id: str, item_id: str) -> Dict[str, Any]:
    """Delete inventory item"""
    try:
        table.delete_item(
            Key={'shopId': shop_id, 'itemId': item_id}
        )
        
        return response(200, {'message': 'Item deleted successfully'})
        
    except Exception as e:
        print(f"Delete item error: {str(e)}")
        return response(500, {'error': 'Failed to delete item'})


def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }
