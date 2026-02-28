import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

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
            shop_id = 'default-shop'
        
        print(f"Processing {method} forecast request for shop: {shop_id}")
        
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
    base_quantity = random.randint(5, 20)
    
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-i)).date()
        quantity = max(0, int(base_quantity + random.randint(-3, 3)))
        
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
    """Simple moving average forecast with festival consideration and realistic trends"""
    if not historical_data:
        return []
    
    quantities = [d['quantity'] for d in historical_data]
    avg = sum(quantities) / len(quantities)
    
    # Calculate trend (simple linear regression)
    n = len(quantities)
    if n >= 3:
        # Calculate slope
        x_mean = (n - 1) / 2
        y_mean = avg
        numerator = sum((i - x_mean) * (quantities[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
    else:
        slope = 0
    
    forecast = []
    for i in range(days):
        date = (datetime.utcnow() + timedelta(days=i+1)).date()
        
        # Base prediction with trend
        base_predicted = avg + (slope * (n + i))
        
        # Add realistic daily variation (±15%)
        daily_variation = random.uniform(-0.15, 0.15)
        predicted = base_predicted * (1 + daily_variation)
        
        # Add weekly pattern (higher on weekends)
        day_of_week = date.weekday()
        is_weekend = day_of_week >= 5  # Saturday or Sunday
        
        # Simple festival detection (major Indian festivals)
        month = date.month
        day = date.day
        is_festival = False
        festival_name = ""
        
        # Approximate festival dates (simplified)
        if (month == 3 and 8 <= day <= 10):  # Holi
            is_festival = True
            festival_name = "Holi"
        elif (month == 10 and 20 <= day <= 25):  # Diwali
            is_festival = True
            festival_name = "Diwali"
        elif (month == 8 and 15 <= day <= 16):  # Independence Day
            is_festival = True
            festival_name = "Independence Day"
        elif (month == 1 and 26 <= day <= 27):  # Republic Day
            is_festival = True
            festival_name = "Republic Day"
        
        # Increase demand for festivals and weekends
        if is_festival:
            predicted = predicted * 1.5  # 50% increase for festivals
        elif is_weekend:
            predicted = predicted * 1.2  # 20% increase for weekends
        
        # Ensure minimum of 1
        predicted = max(1, int(predicted))
        
        forecast.append({
            'date': date.isoformat(),
            'predictedQuantity': predicted,
            'lowerBound': max(0, int(predicted * 0.7)),
            'upperBound': int(predicted * 1.3),
            'isFestival': is_festival,
            'festivalName': festival_name if is_festival else None,
            'isWeekend': is_weekend
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
        mean = sum(quantities) / len(quantities)
        
        if mean == 0:
            return 0.5
        
        # Calculate variance manually
        variance = sum((x - mean) ** 2 for x in quantities) / len(quantities)
        std_dev = variance ** 0.5
        cv = std_dev / mean  # Coefficient of variation
        confidence = max(0.5, min(0.95, 1 - cv/2))
        
        return round(confidence, 2)


def generate_mock_forecast(days: int) -> List[Dict[str, Any]]:
    """Generate mock forecast data"""
    forecast = []
    base = 10
    
    for i in range(days):
        date = (datetime.utcnow() + timedelta(days=i+1)).date()
        predicted = int(base + random.randint(-2, 2))
        
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
