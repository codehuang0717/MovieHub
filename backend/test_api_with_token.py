#!/usr/bin/env python
"""
获取用户token并测试API
"""

import os
import sys
import django
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def get_user_token():
    print("=== 获取用户Token ===")

    # 获取第一个用户
    user = User.objects.first()
    if not user:
        print("没有找到用户！")
        return None, None

    print(f"用户: {user.username}")

    # 生成token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    print(f"Access Token: {access_token}")
    return access_token, refresh


def test_watchlist_api(token):
    print("\n=== 测试想看列表API ===")

    base_url = "http://localhost:8000/api/reviews"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. 获取想看列表
    print("1. 获取想看列表...")
    try:
        response = requests.get(f"{base_url}/watchlist/", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 2. 切换想看状态
    print("\n2. 切换想看状态 (电影ID: 6)...")
    try:
        response = requests.post(f"{base_url}/watchlist/toggle/6/", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 3. 再次获取想看列表
    print("\n3. 再次获取想看列表...")
    try:
        response = requests.get(f"{base_url}/watchlist/", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")


def main():
    print("测试想看列表功能...")

    # 获取token
    access_token, refresh_token = get_user_token()

    if access_token:
        test_watchlist_api(access_token)
    else:
        print("无法获取token，请先运行 create_watchlist_simple.py 创建用户数据")


if __name__ == "__main__":
    main()
