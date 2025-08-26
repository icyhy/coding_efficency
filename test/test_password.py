#!/usr/bin/env python3
"""
测试密码哈希和验证功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.security import get_password_hash, verify_password

def test_password():
    # 测试密码
    test_password = "password123"
    
    # 生成哈希
    hashed = get_password_hash(test_password)
    print(f"原始密码: {test_password}")
    print(f"哈希密码: {hashed}")
    
    # 验证密码
    is_valid = verify_password(test_password, hashed)
    print(f"密码验证结果: {is_valid}")
    
    # 测试错误密码
    wrong_password = "wrongpassword"
    is_wrong_valid = verify_password(wrong_password, hashed)
    print(f"错误密码验证结果: {is_wrong_valid}")
    
    # 测试数据库中的哈希
    db_hash = "$2b$12$U/CMs2CpkjCNgUApVaXQM.yGiLNByzjCFgqbQg/fPWD8qdcDI2UOO"
    db_verify = verify_password(test_password, db_hash)
    print(f"数据库哈希验证结果: {db_verify}")

if __name__ == "__main__":
    test_password()