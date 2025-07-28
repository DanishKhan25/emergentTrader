"""
Simple Authentication Service for EmergentTrader
Hardcoded credentials with JWT token support
"""

import os
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        """Initialize authentication service"""
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
        
        # JWT secret key
        self.jwt_secret = os.getenv('JWT_SECRET', 'emergent_trader_secret_key_2024')
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = 24
        
        logger.info("Authentication service initialized")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
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
            
            # Generate JWT token
            token = self._generate_token(username, user)
            
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
    
    def _generate_token(self, username: str, user: Dict) -> str:
        """Generate JWT token"""
        now = datetime.now()
        payload = {
            'username': username,
            'name': user['name'],
            'role': user['role'],
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=self.token_expiry_hours)).timestamp())
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            return {
                'success': True,
                'user': {
                    'username': payload['username'],
                    'name': payload['name'],
                    'role': payload['role']
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return {
                'success': False,
                'error': 'Token verification failed'
            }
    
    def refresh_token(self, token: str) -> Dict:
        """Refresh JWT token"""
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
            
            # Generate new token
            new_token = self._generate_token(username, self.users[username])
            
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
        """Logout user (in a real system, you'd blacklist the token)"""
        try:
            verification = self.verify_token(token)
            if verification['success']:
                logger.info(f"User {verification['user']['username']} logged out")
                return {
                    'success': True,
                    'message': 'Logged out successfully'
                }
            else:
                return verification
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                'success': False,
                'error': 'Logout failed'
            }

# Global instance
auth_service = AuthService()
