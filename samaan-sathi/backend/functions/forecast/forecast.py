import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np

sagemaker_runtime = boto3.client('sagemaker-runtime')
dynamodb = boto3.resource('dynamodb')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Generate demand forecasts for inventory items
    """
    try:
        method = event.get('httpMethod')
        shop_id = get_shop_id(event)
        
        if not shop_id:
            return response(401, {'error': 'Unauthorized'})
        
        if method == 'GET':
            # Get existing forecasts
            return get_forecasts(shop_id)
        
        elif method == 'POST':
            # Generate new forecasts
            body = json.loads(event.get('body', '{}'))
            item_ids = body.get('itemIds', [])
            days = body.get('days', 14)
            
            return generate_forecasts(shop_id, item_ids, days)
        
        else:
            return response(405, {'error': 'Method not allowed'})
            
    except Exception as e:
        print(f"Forecast Error: {str(e)}")
        return response(500, {'error': str(e)})


def get_shop_id(event: Dict[str, Any]) -> str:
    """Extract shop ID from JWT token"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('custom:shopId', 'default-shop')
    except:
        return None


def get_forecasts(shop_id: str) -> Dict[str, Any]:
    """Get existing forecasts for shop"""
    try:
        # In production, fetch from database
        # For now, return mock data
        forecasts = [
            {
                'itemId': 'item-001',
                'itemName': 'Rice 1kg',
                'forecast': generate_mock_forecast(14),
                'confidence': 0.85,
                'recommendation': 'Stock 50 units for next 2 weeks'
            },
            {
                'itemId': 'item-002',
                'itemName': 'Wheat Flour 1kg',
                'forecast': generate_mock_forecast(14),
                'confidence': 0.78,
                'recommendation': 'Stock 35 units for next 2 weeks'
            }
        ]
        
        return response(200, {
            'shopId': shop_id,
            'forecasts': forecasts,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Get forecasts error: {str(e)}")
        return response(500, {'error': 'Failed to fetch forecasts'})


def generate_forecasts(shop_id: str, item_ids: List[str], days: int) -> Dict[str, Any]:
    """Generate demand forecasts using ML model"""
    try:
        forecasts = []
        
        for item_id in item_ids:
            # Get historical sales data
            historical_data = get_historical_sales(shop_id, item_id)
            
            # Generate forecast
            if len(historical_data) >= 7:
                forecast_data = forecast_with_ml(historical_data, days)
            else:
                # Use simple moving average for insufficient data
                forecast_data = forecast_simple(historical_data, days)
            
            # Generate recommendation
            recommendation = generate_recommendation(forecast_data, historical_data)
            
            forecasts.append({
                'itemId': item_id,
                'forecast': forecast_data,
                'confidence': calculate_confidence(historical_data),
                'recommendation': recommendation
            })
        
        return response(200, {
            'shopId': shop_id,
            'forecasts': forecasts,
            'generatedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Generate forecasts error: {str(e)}")
        return response(500, {'error': 'Failed to generate forecasts'})


def get_historical_sales(shop_id: str, item_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get historical sales data for an item"""
    # In production, query from RDS/DynamoDB
    # For now, generate mock data
    data = []
    base_quantity = np.random.randint(5, 20)
    
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-i)).date()
        quantity = max(0, int(base_quantity + np.random.normal(0, 3)))
        
        data.append({
            'date': date.isoformat(),
            'quantity': quantity
        })
    
    return data


def forecast_with_ml(historical_data: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """Generate forecast using ML model (SageMaker endpoint)"""
    try:
        # In production, call SageMaker endpoint
        # For now, use simple exponential smoothing
        quantities = [d['quantity'] for d in historical_data]
        
        # Simple exponential smoothing
        alpha = 0.3
        forecast = []
        last_value = quantities[-1]
        
        for i in range(days):
            date = (datetime.utcnow() + timedelta(days=i+1)).date()
            predicted = last_value
            
            forecast.append({
                'date': date.isoformat(),
                'predictedQuantity': int(predicted),
                'lowerBound': int(predicted * 0.8),
                'upperBound': int(predicted * 1.2)
            })
        
        return forecast
        
    except Exception as e:
        print(f"ML forecast error: {str(e)}")
        return forecast_simple(historical_data, days)


def forecast_simple(historical_data: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """Simple moving average forecast"""
    if not historical_data:
        return []
    
    quantities = [d['quantity'] for d in historical_data]
    avg = sum(quantities) / len(quantities)
    
    forecast = []
    for i in range(days):
        date = (datetime.utcnow() + timedelta(days=i+1)).date()
        forecast.append({
            'date': date.isoformat(),
            'predictedQuantity': int(avg),
            'lowerBound': int(avg * 0.7),
            'upperBound': int(avg * 1.3)
        })
    
    return forecast


def generate_recommendation(forecast: List[Dict[str, Any]], historical: List[Dict[str, Any]]) -> str:
    """Generate actionable recommendation based on forecast"""
    if not forecast:
        return "Insufficient data for recommendation"
    
    total_predicted = sum(f['predictedQuantity'] for f in forecast)
    avg_daily = total_predicted / len(forecast)
    
    if avg_daily < 5:
        return f"Low demand expected. Stock {int(total_predicted * 1.2)} units for next {len(forecast)} days."
    elif avg_daily > 20:
        return f"High demand expected. Stock {int(total_predicted * 1.3)} units to avoid stock-outs."
    else:
        return f"Moderate demand. Stock {int(total_predicted * 1.1)} units for next {len(forecast)} days."


def calculate_confidence(historical_data: List[Dict[str, Any]]) -> float:
    """Calculate confidence score based on data quality"""
    if len(historical_data) < 7:
        return 0.5
    elif len(historical_data) < 14:
        return 0.7
    else:
        # Calculate based on variance
        quantities = [d['quantity'] for d in historical_data]
        variance = np.var(quantities)
        mean = np.mean(quantities)
        
        if mean == 0:
            return 0.5
        
        cv = np.sqrt(variance) / mean  # Coefficient of variation
        confidence = max(0.5, min(0.95, 1 - cv/2))
        
        return round(confidence, 2)


def generate_mock_forecast(days: int) -> List[Dict[str, Any]]:
    """Generate mock forecast data"""
    forecast = []
    base = 10
    
    for i in range(days):
        date = (datetime.utcnow() + timedelta(days=i+1)).date()
        predicted = int(base + np.random.normal(0, 2))
        
        forecast.append({
            'date': date.isoformat(),
            'predictedQuantity': max(0, predicted),
            'lowerBound': max(0, predicted - 3),
            'upperBound': predicted + 3
        })
    
    return forecast


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
