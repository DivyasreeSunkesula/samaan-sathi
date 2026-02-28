import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, List

bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Generate AI-powered recommendations using Bedrock
    """
    try:
        method = event.get('httpMethod')
        path = event.get('path', '')
        shop_id = get_shop_id(event)
        
        if not shop_id:
            shop_id = 'default-shop'
        
        print(f"Processing {method} recommendations request for shop: {shop_id}")
        
        if method == 'GET':
            return get_recommendations(shop_id)
        elif method == 'POST' and '/generate' in path:
            body = json.loads(event.get('body', '{}'))
            return generate_custom_recommendations(shop_id, body)
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Recommendations Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token - always returns a valid shop_id"""
    try:
        request_context = event.get('requestContext', {})
        if not request_context:
            return 'default-shop'
            
        authorizer = request_context.get('authorizer', {})
        if not authorizer:
            return 'default-shop'
        
        claims = authorizer.get('claims', {})
        if claims:
            shop_id = claims.get('custom:shopId')
            if shop_id:
                return shop_id
            
            username = claims.get('cognito:username') or claims.get('username')
            if username:
                return f"shop-{username}"
        
        return 'default-shop'
    except:
        return 'default-shop'


def get_recommendations(shop_id: str) -> Dict[str, Any]:
    """Get comprehensive recommendations for shop"""
    try:
        # Gather shop data
        shop_data = gather_shop_data(shop_id)
        
        # Generate recommendations using Bedrock
        recommendations = generate_ai_recommendations(shop_data)
        
        return response(200, {
            'shopId': shop_id,
            'recommendations': recommendations,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Get recommendations error: {str(e)}")
        return response(500, {'error': 'Failed to generate recommendations'})


def gather_shop_data(shop_id: str) -> Dict[str, Any]:
    """Gather all relevant shop data for recommendations"""
    try:
        # Get inventory data
        inventory_table = dynamodb.Table(os.environ['INVENTORY_TABLE'])
        inventory_result = inventory_table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id},
            Limit=50
        )
        
        inventory_items = inventory_result.get('Items', [])
        
        # Get udhaar data
        udhaar_table_name = os.environ.get('UDHAAR_TABLE', 'samaan-sathi-udhaar')
        udhaar_table = dynamodb.Table(udhaar_table_name)
        udhaar_result = udhaar_table.query(
            KeyConditionExpression='shopId = :shopId',
            ExpressionAttributeValues={':shopId': shop_id},
            Limit=20
        )
        
        udhaar_records = udhaar_result.get('Items', [])
        
        # Calculate summary metrics
        total_inventory_value = sum(
            float(item.get('quantity', 0)) * float(item.get('costPrice', 0))
            for item in inventory_items
        )
        
        total_udhaar = sum(
            float(record.get('outstandingAmount', 0))
            for record in udhaar_records
        )
        
        low_stock_items = [
            item for item in inventory_items
            if float(item.get('quantity', 0)) < float(item.get('minStockLevel', 0))
        ]
        
        return {
            'inventoryCount': len(inventory_items),
            'totalInventoryValue': round(total_inventory_value, 2),
            'lowStockCount': len(low_stock_items),
            'lowStockItems': [item.get('name') for item in low_stock_items[:5]],
            'totalUdhaar': round(total_udhaar, 2),
            'udhaarCustomers': len(udhaar_records),
            'sampleItems': [
                {
                    'name': item.get('name'),
                    'quantity': float(item.get('quantity', 0)),
                    'price': float(item.get('sellingPrice', 0))
                }
                for item in inventory_items[:10]
            ]
        }
        
    except Exception as e:
        print(f"Gather data error: {str(e)}")
        return {}


def generate_ai_recommendations(shop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendations using Bedrock Claude"""
    try:
        prompt = f"""
        You are an AI retail advisor for small shop owners in India. Analyze this shop data and provide 5 actionable recommendations:
        
        Shop Data:
        - Total inventory items: {shop_data.get('inventoryCount', 0)}
        - Inventory value: ₹{shop_data.get('totalInventoryValue', 0)}
        - Low stock items: {shop_data.get('lowStockCount', 0)} ({', '.join(shop_data.get('lowStockItems', []))})
        - Outstanding udhaar: ₹{shop_data.get('totalUdhaar', 0)} from {shop_data.get('udhaarCustomers', 0)} customers
        
        Provide recommendations in these categories:
        1. Inventory Management
        2. Pricing Strategy
        3. Cash Flow (Udhaar)
        4. Sales Growth
        5. Cost Reduction
        
        For each recommendation, provide:
        - category
        - title (short, actionable)
        - description (2-3 sentences in simple Hindi-English mix)
        - priority (HIGH, MEDIUM, LOW)
        - expectedImpact (brief description)
        
        Return as JSON array only, no explanation.
        """
        
        response_data = bedrock_runtime.invoke_model(
            modelId=os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'temperature': 0.7,
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
            recommendations = json.loads(content[start:end])
            return recommendations
        
        # Fallback recommendations
        return get_fallback_recommendations(shop_data)
        
    except Exception as e:
        print(f"AI recommendations error: {str(e)}")
        return get_fallback_recommendations(shop_data)


def get_fallback_recommendations(shop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fallback recommendations if AI fails"""
    recommendations = []
    
    if shop_data.get('lowStockCount', 0) > 0:
        recommendations.append({
            'category': 'Inventory Management',
            'title': 'Restock Low Inventory Items',
            'description': f"You have {shop_data['lowStockCount']} items running low. Restock {', '.join(shop_data.get('lowStockItems', [])[:3])} to avoid stock-outs.",
            'priority': 'HIGH',
            'expectedImpact': 'Prevent lost sales due to stock-outs'
        })
    
    if shop_data.get('totalUdhaar', 0) > 5000:
        recommendations.append({
            'category': 'Cash Flow',
            'title': 'Recover Outstanding Udhaar',
            'description': f"₹{shop_data['totalUdhaar']} is pending from {shop_data['udhaarCustomers']} customers. Follow up with top 3 customers to improve cash flow.",
            'priority': 'HIGH',
            'expectedImpact': 'Improve working capital by 20-30%'
        })
    
    recommendations.append({
        'category': 'Sales Growth',
        'title': 'Promote Fast-Moving Items',
        'description': 'Identify your top 5 selling items and create combo offers to increase average transaction value.',
        'priority': 'MEDIUM',
        'expectedImpact': 'Increase daily sales by 10-15%'
    })
    
    return recommendations


def generate_custom_recommendations(shop_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Generate custom recommendations based on specific query"""
    try:
        query = body.get('query', '')
        context = body.get('context', {})
        
        if not query:
            return response(400, {'error': 'query required'})
        
        # Gather shop data
        shop_data = gather_shop_data(shop_id)
        
        prompt = f"""
        You are an AI retail advisor. Answer this question for a small shop owner:
        
        Question: {query}
        
        Shop Context:
        {json.dumps(shop_data, indent=2)}
        
        Additional Context:
        {json.dumps(context, indent=2)}
        
        Provide a clear, actionable answer in simple language (Hindi-English mix if appropriate).
        Keep it under 200 words.
        """
        
        response_data = bedrock_runtime.invoke_model(
            modelId=os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'temperature': 0.7,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response_data['body'].read())
        answer = response_body['content'][0]['text']
        
        return response(200, {
            'query': query,
            'answer': answer,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Custom recommendations error: {str(e)}")
        return response(500, {'error': 'Failed to generate custom recommendations'})


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
