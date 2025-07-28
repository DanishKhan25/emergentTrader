"""
Fallback Authentication Service for EmergentTrader
Simple authentication without JWT dependency for development
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FallbackAuthService:
    def __init__(self):
        """Initialize fallback authentication service"""
        # Hardcoded credentials (can be moved to environment variables)
        self.users = {
            "admin": {
                "password": self._hash_password("admin123"),
                "role": "admin",
                "name": "Administrator"
            },
            "trader": {
                "password": self._hash_password("trader123"),
                "role": "trader", 
                "name": "Trader"
            }
        }
        
        # Simple token storage (in production, use Redis or database)
        self.active_tokens = {}
        self.token_expiry_hours = 24
        
        logger.info("Fallback Authentication service initialized")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_simple_token(self, username: str, user: Dict) -> str:
        """Generate simple token without JWT"""
        timestamp = int(time.time())
        token_data = {
            'username': username,
            'name': user['name'],
            'role': user['role'],
            'created_at': timestamp,
            'expires_at': timestamp + (self.token_expiry_hours * 3600)
        }
        
        # Create a simple token (base64 encoded JSON)
        import base64
        token_json = json.dumps(token_data)
        token = base64.b64encode(token_json.encode()).decode()
        
        # Store token
        self.active_tokens[token] = token_data
        
        return token
    
    def authenticate(self, username: str, password: str) -> Dict:
        """Authenticate user with username and password"""
        try:
            if username not in self.users:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            user = self.users[username]
            hashed_password = self._hash_password(password)
            
            if user['password'] != hashed_password:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Generate simple token
            token = self._generate_simple_token(username, user)
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'username': username,
                    'name': user['name'],
                    'role': user['role']
                },
                'expires_at': (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                'success': False,
                'error': 'Authentication failed'
            }
    
    def verify_token(self, token: str) -> Dict:
        """Verify simple token"""
        try:
            if token not in self.active_tokens:
                return {
                    'success': False,
                    'error': 'Invalid token'
                }
            
            token_data = self.active_tokens[token]
            current_time = int(time.time())
            
            # Check if token is expired
            if current_time > token_data['expires_at']:
                # Remove expired token
                del self.active_tokens[token]
                return {
                    'success': False,
                    'error': 'Token has expired'
                }
            
            return {
                'success': True,
                'user': {
                    'username': token_data['username'],
                    'name': token_data['name'],
                    'role': token_data['role']
                }
            }
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return {
                'success': False,
                'error': 'Token verification failed'
            }
    
    def refresh_token(self, token: str) -> Dict:
        """Refresh simple token"""
        try:
            # Verify current token
            verification = self.verify_token(token)
            if not verification['success']:
                return verification
            
            user_data = verification['user']
            username = user_data['username']
            
            if username not in self.users:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Remove old token
            if token in self.active_tokens:
                del self.active_tokens[token]
            
            # Generate new token
            new_token = self._generate_simple_token(username, self.users[username])
            
            return {
                'success': True,
                'token': new_token,
                'user': user_data,
                'expires_at': (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {
                'success': False,
                'error': 'Token refresh failed'
            }
    
    def logout(self, token: str) -> Dict:
        """Logout user"""
        try:
            if token in self.active_tokens:
                username = self.active_tokens[token]['username']
                del self.active_tokens[token]
                logger.info(f"User {username} logged out")
            
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                'success': False,
                'error': 'Logout failed'
            }

# Global instance
fallback_auth_service = FallbackAuthService()
