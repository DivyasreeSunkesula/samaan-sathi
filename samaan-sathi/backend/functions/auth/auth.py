import json
import os
import boto3
from typing import Dict, Any

cognito = boto3.client('cognito-idp')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle authentication requests (login, register, simple password reset)
    """
    try:
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}'))
        
        # Check if this is a password reset request (using register endpoint)
        if body.get('_action') == 'reset-password':
            return simple_reset_password(body)
        
        if '/login' in path:
            return login(body)
        elif '/register' in path:
            return register(body)
        elif '/simple-reset-password' in path:
            return simple_reset_password(body)
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
        
        # Use USER_PASSWORD_AUTH flow (no SRP required)
        response_data = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        return response(200, {
            'accessToken': response_data['AuthenticationResult']['AccessToken'],
            'idToken': response_data['AuthenticationResult']['IdToken'],
            'refreshToken': response_data['AuthenticationResult']['RefreshToken'],
            'expiresIn': response_data['AuthenticationResult']['ExpiresIn'],
            'message': 'Login successful'
        })
        
    except cognito.exceptions.NotAuthorizedException:
        return response(401, {'error': 'Invalid username or password'})
    except cognito.exceptions.UserNotConfirmedException:
        return response(403, {'error': 'User not confirmed. Please check your email.'})
    except Exception as e:
        print(f"Login error: {str(e)}")
        return response(500, {'error': f'Login failed: {str(e)}'})


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
        # Get client ID and pool ID from environment
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        if not client_id or not user_pool_id:
            return response(500, {'error': 'Configuration error: CLIENT_ID or POOL_ID not set'})
        
        print(f"Registering user: {username}")
        print(f"User Pool ID: {user_pool_id}")
        
        # Create user in Cognito
        user_attributes = [
            {'Name': 'email', 'Value': email},
            {'Name': 'phone_number', 'Value': phone},
            {'Name': 'name', 'Value': full_name},
        ]
        
        if shop_name:
            user_attributes.append({'Name': 'custom:shopName', 'Value': shop_name})
        
        # Sign up user
        signup_response = cognito.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            UserAttributes=user_attributes
        )
        
        print(f"User {username} signed up successfully")
        
        # CRITICAL: Auto-confirm the user immediately
        # This is essential for seamless user experience
        try:
            confirm_response = cognito.admin_confirm_sign_up(
                UserPoolId=user_pool_id,
                Username=username
            )
            print(f"✓ User {username} AUTO-CONFIRMED successfully")
            print(f"Confirm response: {confirm_response}")
            
            # Verify user is confirmed
            user_info = cognito.admin_get_user(
                UserPoolId=user_pool_id,
                Username=username
            )
            user_status = user_info.get('UserStatus')
            print(f"User status after confirm: {user_status}")
            
            if user_status != 'CONFIRMED':
                print(f"WARNING: User status is {user_status}, not CONFIRMED!")
            
        except Exception as confirm_error:
            print(f"ERROR: Auto-confirm failed for {username}: {str(confirm_error)}")
            import traceback
            traceback.print_exc()
            # Return error so user knows to contact admin
            return response(500, {
                'error': 'Registration completed but auto-confirmation failed. Please contact administrator.',
                'username': username,
                'details': str(confirm_error)
            })
        
        return response(201, {
            'message': 'User registered and confirmed successfully. You can now login.',
            'username': username,
            'autoConfirmed': True
        })
        
    except cognito.exceptions.UsernameExistsException:
        return response(409, {'error': 'Username already exists'})
    except cognito.exceptions.InvalidPasswordException as e:
        return response(400, {'error': str(e)})
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': f'Registration failed: {str(e)}'})


def simple_reset_password(body: Dict[str, Any]) -> Dict[str, Any]:
    """Simple password reset - verify username and email, then set new password"""
    username = body.get('username')
    email = body.get('email')
    new_password = body.get('newPassword')
    
    if not all([username, email, new_password]):
        return response(400, {'error': 'Username, email, and new password are required'})
    
    try:
        user_pool_id = os.environ.get('USER_POOL_ID')
        if not user_pool_id:
            return response(500, {'error': 'Configuration error: POOL_ID not set'})
        
        print(f"Simple password reset for user: {username}")
        
        # Get user info to verify email
        try:
            user_info = cognito.admin_get_user(
                UserPoolId=user_pool_id,
                Username=username
            )
            
            # Find email attribute
            user_email = None
            for attr in user_info.get('UserAttributes', []):
                if attr['Name'] == 'email':
                    user_email = attr['Value']
                    break
            
            # Verify email matches
            if not user_email or user_email.lower() != email.lower():
                return response(400, {'error': 'Username and email do not match'})
            
            print(f"Email verified for {username}")
            
        except cognito.exceptions.UserNotFoundException:
            return response(404, {'error': 'User not found'})
        
        # Set new password (admin privilege)
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=new_password,
            Permanent=True
        )
        
        print(f"Password reset successful for {username}")
        
        return response(200, {
            'message': 'Password reset successful. You can now login with your new password.',
            'username': username
        })
        
    except cognito.exceptions.InvalidPasswordException as e:
        return response(400, {'error': str(e)})
    except cognito.exceptions.UserNotFoundException:
        return response(404, {'error': 'User not found'})
    except Exception as e:
        print(f"Simple reset password error: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': f'Failed to reset password: {str(e)}'})


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
