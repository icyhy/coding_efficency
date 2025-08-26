import base64
import json

def decode_jwt_payload(token):
    """解码JWT token的payload部分"""
    try:
        # JWT token由三部分组成，用.分隔
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 获取payload部分（第二部分）
        payload = parts[1]
        
        # 添加必要的padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Base64解码
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # 解析JSON
        payload_data = json.loads(decoded_str)
        return payload_data
    except Exception as e:
        print(f"解码错误: {e}")
        return None

if __name__ == "__main__":
    # 测试token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYyMDIxODAsInN1YiI6IjEifQ.6sn9QjXJhZQoCjjU9RSVbVyPEcHY_DrlS0DXkqBJPiw"
    
    payload = decode_jwt_payload(token)
    if payload:
        print("JWT Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"\nUser ID (sub): {payload.get('sub')}")
        print(f"User ID type: {type(payload.get('sub'))}")
    else:
        print("无法解码JWT token")