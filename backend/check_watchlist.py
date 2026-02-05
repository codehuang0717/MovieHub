#!/usr/bin/env python
"""
检查想看列表数据
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


def check_data():
    print("=== 检查数据库数据 ===")

    # 1. 检查用户
    users = User.objects.all()
    print(f"用户总数: {users.count()}")
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")

    if not users.exists():
        print("❌ 没有用户！")
        return

    # 2. 检查电影
    movies = Movie.objects.all()
    print(f"\n电影总数: {movies.count()}")
    for movie in movies[:5]:  # 只显示前5个
        print(f"  - {movie.title} (ID: {movie.id})")

    if not movies.exists():
        print("❌ 没有电影！")
        return

    # 3. 检查所有想看列表
    all_watchlists = Watchlist.objects.all()
    print(f"\n所有想看列表总数: {all_watchlists.count()}")
    for wl in all_watchlists:
        print(f"  - 用户: {wl.user.username}, 电影: {wl.movie.title} (ID: {wl.id})")

    # 4. 检查特定用户的想看列表
    user = users.first()
    user_watchlist = Watchlist.objects.filter(user=user).select_related("movie")
    print(f"\n用户 {user.username} 的想看列表:")
    print(f"  数量: {user_watchlist.count()}")
    for wl in user_watchlist:
        print(f"  - {wl.movie.title} (状态: {wl.status}, ID: {wl.id})")

    # 5. 手动创建一个想看列表项用于测试
    if user_watchlist.count() == 0 and movies.exists():
        movie = movies.first()
        print(f"\n🧪 为用户 {user.username} 创建想看列表项...")
        print(f"选择电影: {movie.title} (ID: {movie.id})")

        try:
            watchlist_item = Watchlist.objects.create(
                user=user, movie=movie, status="want_to_watch"
            )
            print(f"✅ 成功创建想看列表项，ID: {watchlist_item.id}")

            # 验证创建
            created_watchlist = Watchlist.objects.filter(user=user).select_related(
                "movie"
            )
            print(f"✅ 验证：用户想看列表数量: {created_watchlist.count()}")
            for item in created_watchlist:
                print(f"  - {item.movie.title} (状态: {item.status})")

        except Exception as e:
            print(f"❌ 创建失败: {e}")


if __name__ == "__main__":
    check_data()
