#!/usr/bin/env python
"""
测试想看列表功能的脚本
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from reviews.models import Watchlist
from movies.models import Movie


def test_watchlist():
    print("=== 测试想看列表功能 ===")

    # 1. 检查数据库中是否有用户
    users = User.objects.all()
    print(f"用户总数: {users.count()}")

    if not users.exists():
        print("没有找到用户，请先注册用户")
        return

    # 2. 检查电影数据
    movies = Movie.objects.all()
    print(f"电影总数: {movies.count()}")

    if not movies.exists():
        print("没有找到电影，请先同步电影数据")
        return

    # 3. 获取第一个用户和电影进行测试
    user = users.first()
    movie = movies.first()

    print(f"\n测试用户: {user.username}")
    print(f"测试电影: {movie.title} (ID: {movie.id})")

    # 4. 测试添加到想看列表
    try:
        watchlist_item, created = Watchlist.objects.get_or_create(
            user=user, movie=movie, defaults={"status": "want_to_watch"}
        )

        if created:
            print("成功添加到想看列表")
        else:
            print(f"电影已在想看列表中，状态: {watchlist_item.status}")
    except Exception as e:
        print(f"添加失败: {e}")
        return
    
    # 5. 查询用户的想看列表
    try:
        user_watchlist = Watchlist.objects.filter(user=user).select_related('movie')
        print(f"用户 {user.username} 的想看列表:")
        for item in user_watchlist:
            print(f"  - {item.movie.title} (状态: {item.status})")
    except Exception as e:
        print(f"查询失败: {e}")
    
    # 6. 测试移除操作
    try:
        Watchlist.objects.filter(user=user, movie=movie).delete()
        print("成功从想看列表移除")
    except Exception as e:
        print(f"移除失败: {e}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_watchlist()
