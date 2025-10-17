#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local AI - Authentication Manager
Manages HuggingFace tokens from file and environment
"""

import os
from pathlib import Path
from typing import Optional


class AuthManager:
    """Manage HuggingFace authentication tokens"""
    
    def __init__(self, token_file: str = "config/auth/hf_token.txt"):
        self.token_file = Path(token_file)
        self._token: Optional[str] = None
    
    def load_token(self) -> Optional[str]:
        """
        Load token from file or environment
        Priority: File > Environment
        """
        # Try to load from file first
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token and token.startswith('hf_'):
                        self._token = token
                        return token
            except Exception as e:
                print(f"⚠️ Failed to read token file: {e}")
        
        # Fallback to environment variables
        token = os.getenv('HUGGINGFACE_HUB_TOKEN') or os.getenv('HF_TOKEN')
        if token:
            self._token = token
            return token
        
        return None
    
    def save_token(self, token: str) -> bool:
        """Save token to file"""
        try:
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(token.strip())
            self._token = token
            return True
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            return False
    
    def get_token(self) -> Optional[str]:
        """Get current token (cached or load)"""
        if self._token:
            return self._token
        return self.load_token()
    
    def validate_token(self) -> bool:
        """Validate token with HuggingFace"""
        token = self.get_token()
        if not token:
            return False
        
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=token)
            api.whoami()
            return True
        except Exception as e:
            print(f"❌ Token validation failed: {e}")
            return False
    
    def get_user_info(self) -> dict:
        """Get logged in user info"""
        token = self.get_token()
        if not token:
            return {"logged_in": False}
        
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=token)
            user = api.whoami()
            return {
                "logged_in": True,
                "username": user.get("name"),
                "email": user.get("email"),
                "type": user.get("type")
            }
        except Exception as e:
            return {"logged_in": False, "error": str(e)}
    
    def set_env_token(self):
        """Set token in environment variables"""
        token = self.get_token()
        if token:
            os.environ['HUGGINGFACE_HUB_TOKEN'] = token
            os.environ['HF_TOKEN'] = token
            return True
        return False


# Global instance
AUTH_MANAGER = AuthManager()


if __name__ == "__main__":
    # Test auth manager
    auth = AuthManager()
    
    print("Loading token...")
    token = auth.load_token()
    
    if token:
        print(f"✅ Token loaded: {token[:10]}...")
        
        print("\nValidating token...")
        if auth.validate_token():
            print("✅ Token is valid")
            
            print("\nUser info:")
            info = auth.get_user_info()
            print(info)
        else:
            print("❌ Token is invalid")
    else:
        print("❌ No token found")

