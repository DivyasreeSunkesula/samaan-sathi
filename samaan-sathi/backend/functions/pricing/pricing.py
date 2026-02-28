import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Generate pricing recommendations based on demand and competition
    """
    try:
        path = event.get('path', '')
        shop_id = get_shop_id(event)
        
        if not shop_id:
            return response(401, {'error': 'Unauthorized'})
        
        if '/recommendations' in path:
            return get_pricing_recommendations(shop_id)
        elif '/optimize' in path:
            body = json.loads(event.get('body', '{}'))
            return optimize_pricing(shop_id, body)
        else:
            return response(400, {'error': 'Invalid endpoint'})
            
    except Exception as e:
        print(f"Pricing Error: {str(e)}")
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('custom:shopId', 'default-shop')
    except:
        return None


def get_pricing_recommendations(shop_id: str) -> Dict[str, Any]:
    """Get pricing recommendations for all items"""
    try:
        # Get inventory items
        table = dynamodb.Table(os.environ['INVENTORY_TABLE'])
        result = table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id}
        )
        
        items = result.get('Items', [])
        recommendations = []
        
        for item in items:
            rec = analyze_item_pricing(item)
            if rec:
                recommendations.append(rec)
        
        return response(200, {
            'shopId': shop_id,
            'recommendations': recommendations,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Get recommendations error: {str(e)}")
        return response(500, {'error': 'Failed to get recommendations'})


def analyze_item_pricing(item: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze pricing for a single item"""
    try:
        cost_price = float(item.get('costPrice', 0))
        selling_price = float(item.get('sellingPrice', 0))
        quantity = float(item.get('quantity', 0))
        
        if cost_price == 0 or selling_price == 0:
            return None
        
        # Calculate current margin
        margin = ((selling_price - cost_price) / selling_price) * 100
        
        # Determine recommendation
        action = None
        suggested_price = selling_price
        reason = ""
        
        if margin < 10:
            action = "INCREASE"
            suggested_price = cost_price * 1.15  # 15% margin
            reason = "Low margin detected. Increase price to improve profitability."
        elif margin > 40:
            action = "DECREASE"
            suggested_price = cost_price * 1.25  # 25% margin
            reason = "High margin may reduce sales. Consider price reduction to increase volume."
        elif quantity < float(item.get('minStockLevel', 0)):
            action = "INCREASE"
            suggested_price = selling_price * 1.05
            reason = "Low stock. Slight price increase to manage demand."
        else:
            action = "MAINTAIN"
            reason = "Current pricing is optimal."
        
        return {
            'itemId': item['itemId'],
            'itemName': item.get('name', 'Unknown'),
            'currentPrice': selling_price,
            'suggestedPrice': round(suggested_price, 2),
            'currentMargin': round(margin, 2),
            'suggestedMargin': round(((suggested_price - cost_price) / suggested_price) * 100, 2),
            'action': action,
            'reason': reason,
            'confidence': 0.75
        }
        
    except Exception as e:
        print(f"Analyze pricing error: {str(e)}")
        return None


def optimize_pricing(shop_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize pricing using AI"""
    try:
        item_ids = body.get('itemIds', [])
        
        if not item_ids:
            return response(400, {'error': 'itemIds required'})
        
        # Get items from database
        table = dynamodb.Table(os.environ['INVENTORY_TABLE'])
        items = []
        
        for item_id in item_ids:
            result = table.get_item(
                Key={'shopId': shop_id, 'itemId': item_id}
            )
            if 'Item' in result:
                items.append(result['Item'])
        
        # Use Bedrock for advanced pricing optimization
        optimized = optimize_with_ai(items)
        
        return response(200, {
            'shopId': shop_id,
            'optimizedPricing': optimized,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Optimize pricing error: {str(e)}")
        return response(500, {'error': 'Failed to optimize pricing'})


def optimize_with_ai(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Use Bedrock to optimize pricing"""
    try:
        items_data = []
        for item in items:
            items_data.append({
                'id': item['itemId'],
                'name': item.get('name'),
                'costPrice': float(item.get('costPrice', 0)),
                'sellingPrice': float(item.get('sellingPrice', 0)),
                'quantity': float(item.get('quantity', 0)),
                'category': item.get('category')
            })
        
        prompt = f"""
        As a retail pricing expert, analyze these products and provide pricing recommendations:
        
        {json.dumps(items_data, indent=2)}
        
        For each item, provide:
        1. Suggested price (considering 15-30% margin)
        2. Pricing strategy (premium, competitive, or discount)
        3. Brief explanation
        
        Return as JSON array with: itemId, suggestedPrice, strategy, explanation
        """
        
        response_data = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response_data['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        start = content.find('[')
        end = content.rfind(']') + 1
        if start >= 0 and end > start:
            optimized = json.loads(content[start:end])
            return optimized
        
        # Fallback to simple analysis
        return [analyze_item_pricing(item) for item in items]
        
    except Exception as e:
        print(f"AI optimization error: {str(e)}")
        return [analyze_item_pricing(item) for item in items]


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
        'body': json.dumps(body)
    }
