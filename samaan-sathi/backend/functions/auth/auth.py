import json
import os
import boto3
from typing import Dict, Any

cognito = boto3.client('cognito-idp')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle authentication requests (login, register, refresh token)
    """
    try:
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}'))
        
        if '/login' in path:
            return login(body)
        elif '/register' in path:
            return register(body)
        else:
            return response(400, {'error': 'Invalid endpoint'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': str(e)})


def login(body: Dict[str, Any]) -> Dict[str, Any]:
    """Login user with username/email and password"""
    username = body.get('username')
    password = body.get('password')
    
    if not username or not password:
        return response(400, {'error': 'Username and password required'})
    
    try:
        # Get client ID from environment
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        if not client_id:
            return response(500, {'error': 'Configuration error: CLIENT_ID not set'})
        
        # Initiate auth with Cognito
        response_data = cognito.admin_initiate_auth(
            UserPoolId=os.environ['USER_POOL_ID'],
            ClientId=client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        return response(200, {
            'accessToken': response_data['AuthenticationResult']['AccessToken'],
            'idToken': response_data['AuthenticationResult']['IdToken'],
            'refreshToken': response_data['AuthenticationResult']['RefreshToken'],
            'expiresIn': response_data['AuthenticationResult']['ExpiresIn']
        })
        
    except cognito.exceptions.NotAuthorizedException:
        return response(401, {'error': 'Invalid credentials'})
    except Exception as e:
        print(f"Login error: {str(e)}")
        return response(500, {'error': 'Login failed'})


def register(body: Dict[str, Any]) -> Dict[str, Any]:
    """Register new user"""
    username = body.get('username')
    password = body.get('password')
    email = body.get('email')
    phone = body.get('phone')
    full_name = body.get('fullName')
    shop_name = body.get('shopName')
    
    if not all([username, password, email, phone, full_name]):
        return response(400, {'error': 'Missing required fields'})
    
    try:
        # Get client ID from environment
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        if not client_id:
            return response(500, {'error': 'Configuration error: CLIENT_ID not set'})
        
        # Create user in Cognito
        user_attributes = [
            {'Name': 'email', 'Value': email},
            {'Name': 'phone_number', 'Value': phone},
            {'Name': 'name', 'Value': full_name},
        ]
        
        if shop_name:
            user_attributes.append({'Name': 'custom:shopName', 'Value': shop_name})
        
        cognito.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            UserAttributes=user_attributes
        )
        
        return response(201, {
            'message': 'User registered successfully',
            'username': username
        })
        
    except cognito.exceptions.UsernameExistsException:
        return response(409, {'error': 'Username already exists'})
    except cognito.exceptions.InvalidPasswordException as e:
        return response(400, {'error': str(e)})
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return response(500, {'error': 'Registration failed'})


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
        'body': json.dumps(body)
    }
