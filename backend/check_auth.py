#!/usr/bin/env python
"""
检查用户认证状态
"""

import os
import sys
import django


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def check_auth():
    print("=== 检查用户认证状态 ===")

    users = User.objects.all()
    print(f"数据库中的用户:")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")

    if not users.exists():
        print("❌ 数据库中没有用户！")
        return None

    # 获取第一个用户的token
    user = users.first()
    print(f"\n生成Token的用户: {user.username}")

    # 生成有效的token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    print(f"\n生成的Access Token:")
    print(f"{access_token[:50]}...")  # 只显示前50个字符
    print(f"Token长度: {len(access_token)}")

    # 验证token
    try:
        from rest_framework_simplejwt.authentication import JWTAuthentication

        jwt_auth = JWTAuthentication()

        # 创建模拟请求
        class MockRequest:
            def __init__(self, token):
                self.META = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        # 测试token验证
        mock_request = MockRequest(access_token)
        validated_user = jwt_auth.authenticate(mock_request)

        print(f"\nToken验证成功:")
        print(f"  用户名: {validated_user.username}")
        print(f"  用户ID: {validated_user.id}")

        return access_token

    except Exception as e:
        print(f"\nToken验证失败: {e}")
        return access_token


if __name__ == "__main__":
    token = check_auth()
    print(f"\n=== 可以使用以下信息登录 ===")
    print(f"用户名: {users.first().username}")
    print(f"密码: 如果是默认密码，可能是 admin123")
    print(f"Token: {token}")
    print(f"登录URL: http://localhost:5173/login")
