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
        
        # shop_id should never be None now, but double check
        if not shop_id:
            print("ERROR: shop_id is None or empty!")
            shop_id = 'default-shop'
        
        print(f"Processing {method} request for shop: {shop_id}")
        print(f"Path: {path}")
        
        if method == 'GET':
            if '{itemId}' in path or path.endswith('/inventory/'):
                # Check if itemId in pathParameters
                path_params = event.get('pathParameters') or {}
                item_id = path_params.get('itemId')
                if item_id:
                    return get_item(shop_id, item_id)
                else:
                    return get_all_items(shop_id, event.get('queryStringParameters') or {})
            else:
                return get_all_items(shop_id, event.get('queryStringParameters') or {})
        
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            
            # Check if this is a delete operation
            if body.get('_action') == 'delete' and body.get('itemId'):
                return delete_item(shop_id, body['itemId'])
            
            return add_or_update_item(shop_id, body)
        
        elif method == 'DELETE':
            path_params = event.get('pathParameters') or {}
            item_id = path_params.get('itemId')
            if not item_id:
                return response(400, {'error': 'itemId required'})
            return delete_item(shop_id, item_id)
        
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token - always returns a valid shop_id"""
    try:
        # Try to get from authorizer context
        request_context = event.get('requestContext', {})
        if not request_context:
            print("No requestContext found, using default-shop")
            return 'default-shop'
            
        authorizer = request_context.get('authorizer', {})
        if not authorizer:
            print("No authorizer found, using default-shop")
            return 'default-shop'
        
        # Try claims first
        claims = authorizer.get('claims', {})
        if claims:
            # Try custom attribute
            shop_id = claims.get('custom:shopId')
            if shop_id:
                print(f"Found shop_id from custom attribute: {shop_id}")
                return shop_id
            
            # Try username as fallback
            username = claims.get('cognito:username') or claims.get('username')
            if username:
                shop_id = f"shop-{username}"
                print(f"Using username-based shop_id: {shop_id}")
                return shop_id
        
        # Fallback to default shop
        print("No claims found, using default-shop")
        return 'default-shop'
    except Exception as e:
        print(f"Error getting shop_id: {str(e)}, using default-shop")
        return 'default-shop'


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
