# -*- coding: utf-8 -*-
"""
加密解密工具函数
用于API密钥等敏感数据的安全存储
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app
from typing import Optional

class CryptoManager:
    """
    加密管理器类
    处理数据的加密和解密操作
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化加密管理器
        
        Args:
            secret_key (str): 密钥，如果为None则从配置中获取
        """
        self.secret_key = secret_key or self._get_secret_key()
        self._fernet = None
    
    def _get_secret_key(self) -> str:
        """
        获取密钥
        
        Returns:
            str: 密钥
        """
        try:
            # 优先从Flask配置获取
            if current_app:
                return current_app.config.get('SECRET_KEY', 'default-secret-key')
        except RuntimeError:
            # 如果不在Flask应用上下文中，从环境变量获取
            pass
        
        return os.environ.get('SECRET_KEY', 'default-secret-key')
    
    def _get_fernet(self) -> Fernet:
        """
        获取Fernet加密实例
        
        Returns:
            Fernet: 加密实例
        """
        if self._fernet is None:
            # 使用PBKDF2从密钥派生加密密钥
            password = self.secret_key.encode()
            salt = b'coding_efficiency_salt'  # 在生产环境中应该使用随机盐
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt(self, data: str) -> str:
        """
        加密数据
        
        Args:
            data (str): 要加密的数据
        
        Returns:
            str: 加密后的数据（Base64编码）
        """
        if not data:
            return ''
        
        try:
            fernet = self._get_fernet()
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            current_app.logger.error(f"数据加密失败: {str(e)}")
            raise ValueError("数据加密失败")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data (str): 加密的数据（Base64编码）
        
        Returns:
            str: 解密后的数据
        """
        if not encrypted_data:
            return ''
        
        try:
            fernet = self._get_fernet()
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            current_app.logger.error(f"数据解密失败: {str(e)}")
            raise ValueError("数据解密失败")
    
    def is_encrypted(self, data: str) -> bool:
        """
        检查数据是否已加密
        
        Args:
            data (str): 要检查的数据
        
        Returns:
            bool: 是否已加密
        """
        if not data:
            return False
        
        try:
            # 尝试解密，如果成功则说明已加密
            self.decrypt(data)
            return True
        except Exception:
            return False

# 全局加密管理器实例
_crypto_manager = None

def get_crypto_manager() -> CryptoManager:
    """
    获取全局加密管理器实例
    
    Returns:
        CryptoManager: 加密管理器实例
    """
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager

def encrypt_data(data: str) -> str:
    """
    加密数据（便捷函数）
    
    Args:
        data (str): 要加密的数据
    
    Returns:
        str: 加密后的数据
    """
    return get_crypto_manager().encrypt(data)

def decrypt_data(encrypted_data: str) -> str:
    """
    解密数据（便捷函数）
    
    Args:
        encrypted_data (str): 加密的数据
    
    Returns:
        str: 解密后的数据
    """
    return get_crypto_manager().decrypt(encrypted_data)

def is_data_encrypted(data: str) -> bool:
    """
    检查数据是否已加密（便捷函数）
    
    Args:
        data (str): 要检查的数据
    
    Returns:
        bool: 是否已加密
    """
    return get_crypto_manager().is_encrypted(data)

def generate_encryption_key() -> str:
    """
    生成新的加密密钥
    
    Returns:
        str: Base64编码的密钥
    """
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """
    哈希密码
    
    Args:
        password (str): 原始密码
        salt (str): 盐值，如果为None则生成新盐值
    
    Returns:
        tuple: (哈希值, 盐值)
    """
    import hashlib
    import secrets
    
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 使用PBKDF2进行密码哈希
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    )
    
    return password_hash.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    验证密码
    
    Args:
        password (str): 原始密码
        password_hash (str): 存储的哈希值
        salt (str): 盐值
    
    Returns:
        bool: 密码是否正确
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash

def generate_api_key(length: int = 32) -> str:
    """
    生成API密钥
    
    Args:
        length (int): 密钥长度
    
    Returns:
        str: API密钥
    """
    import secrets
    import string
    
    # 使用字母和数字生成API密钥
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    遮蔽敏感数据
    
    Args:
        data (str): 敏感数据
        mask_char (str): 遮蔽字符
        visible_chars (int): 可见字符数
    
    Returns:
        str: 遮蔽后的数据
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ''
    
    visible_part = data[:visible_chars]
    masked_part = mask_char * (len(data) - visible_chars)
    
    return visible_part + masked_part

def secure_compare(a: str, b: str) -> bool:
    """
    安全比较两个字符串（防止时序攻击）
    
    Args:
        a (str): 字符串A
        b (str): 字符串B
    
    Returns:
        bool: 是否相等
    """
    import hmac
    
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    
    return hmac.compare_digest(a.encode(), b.encode())

class TokenManager:
    """
    令牌管理器
    用于生成和验证各种类型的令牌
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化令牌管理器
        
        Args:
            secret_key (str): 密钥
        """
        self.crypto_manager = CryptoManager(secret_key)
    
    def generate_reset_token(self, user_id: int, expires_in: int = 3600) -> str:
        """
        生成密码重置令牌
        
        Args:
            user_id (int): 用户ID
            expires_in (int): 过期时间（秒）
        
        Returns:
            str: 重置令牌
        """
        import time
        import json
        
        payload = {
            'user_id': user_id,
            'type': 'password_reset',
            'expires_at': time.time() + expires_in
        }
        
        return self.crypto_manager.encrypt(json.dumps(payload))
    
    def verify_reset_token(self, token: str) -> Optional[int]:
        """
        验证密码重置令牌
        
        Args:
            token (str): 重置令牌
        
        Returns:
            int: 用户ID，如果令牌无效则返回None
        """
        import time
        import json
        
        try:
            payload_str = self.crypto_manager.decrypt(token)
            payload = json.loads(payload_str)
            
            # 检查令牌类型
            if payload.get('type') != 'password_reset':
                return None
            
            # 检查是否过期
            if time.time() > payload.get('expires_at', 0):
                return None
            
            return payload.get('user_id')
            
        except Exception:
            return None
    
    def generate_email_verification_token(self, user_id: int, email: str, expires_in: int = 86400) -> str:
        """
        生成邮箱验证令牌
        
        Args:
            user_id (int): 用户ID
            email (str): 邮箱地址
            expires_in (int): 过期时间（秒）
        
        Returns:
            str: 验证令牌
        """
        import time
        import json
        
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'email_verification',
            'expires_at': time.time() + expires_in
        }
        
        return self.crypto_manager.encrypt(json.dumps(payload))
    
    def verify_email_verification_token(self, token: str) -> Optional[tuple]:
        """
        验证邮箱验证令牌
        
        Args:
            token (str): 验证令牌
        
        Returns:
            tuple: (用户ID, 邮箱)，如果令牌无效则返回None
        """
        import time
        import json
        
        try:
            payload_str = self.crypto_manager.decrypt(token)
            payload = json.loads(payload_str)
            
            # 检查令牌类型
            if payload.get('type') != 'email_verification':
                return None
            
            # 检查是否过期
            if time.time() > payload.get('expires_at', 0):
                return None
            
            return payload.get('user_id'), payload.get('email')
            
        except Exception:
            return None

# 全局令牌管理器实例
_token_manager = None

def get_token_manager() -> TokenManager:
    """
    获取全局令牌管理器实例
    
    Returns:
        TokenManager: 令牌管理器实例
    """
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager