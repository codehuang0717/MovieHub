#!/usr/bin/env python
"""
测试想看列表API
"""

import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from reviews.views import WatchlistListCreateView, ToggleWatchlistView


def test_watchlist_api():
    print("=== 测试想看列表API ===")

    # 创建用户和请求工厂
    user = User.objects.first()
    factory = RequestFactory()

    # 测试获取想看列表
    print("\n1. 测试获取想看列表...")
    request = factory.get("/api/reviews/watchlist/")
    request.user = user

    view = WatchlistListCreateView()
    view.setup(request)

    response = view.get(request)
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    # 测试切换想看状态
    print("\n2. 测试切换想看状态...")
    movie_id = 6  # Avengers: Endgame

    request = factory.post(f"/api/reviews/watchlist/toggle/{movie_id}/")
    request.user = user

    view = ToggleWatchlistView()
    view.setup(request)

    response = view.post(request, movie_id=movie_id)
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.data, indent=2, ensure_ascii=False)}")

    # 再次获取想看列表
    print("\n3. 再次获取想看列表...")
    request = factory.get("/api/reviews/watchlist/")
    request.user = user

    view = WatchlistListCreateView()
    view.setup(request)

    response = view.get(request)
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.data, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    test_watchlist_api()
