#!/usr/bin/env python
"""
为用户创建想看列表数据
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


def create_watchlist_data():
    print("=== 为所有用户创建想看列表数据 ===")

    users = User.objects.all()
    movies = Movie.objects.all()

    if not users.exists():
        print("❌ 没有用户！")
        return

    if not movies.exists():
        print("❌ 没有电影！")
        return

    # 为每个用户创建想看列表
    user_watchlists = {}

    for user in users:
        user_watchlists[user.username] = []
        print(f"\n为用户 {user.username} 创建想看列表:")

        # 为每个用户添加3-4部电影到想看列表
        # 避免重复使用相同的电影
        start_index = (users.filter(id__lt=user.id).count() * 3) % movies.count()

        for i in range(min(4, movies.count() - start_index)):
            movie_index = (start_index + i) % movies.count()
            movie = movies[movie_index]

            # 检查是否已经存在
            if not Watchlist.objects.filter(user=user, movie=movie).exists():
                try:
                    # 根据用户ID分配不同的状态
                    status_choices = ["want_to_watch", "watching", "watched"]
                    status = status_choices[i % len(status_choices)]

                    watchlist_item = Watchlist.objects.create(
                        user=user, movie=movie, status=status
                    )

                    user_watchlists[user.username].append(
                        {
                            "movie": movie.title,
                            "status": status,
                            "id": watchlist_item.id,
                        }
                    )

                    print(f"  ✅ 添加: {movie.title} (状态: {status})")

                except Exception as e:
                    print(f"  ❌ 添加失败 {movie.title}: {e}")

    # 打印最终的想看列表统计
    print(f"\n=== 想看列表统计 ===")
    for user in users:
        user_count = Watchlist.objects.filter(user=user).count()
        print(f"{user.username}: {user_count} 个想看列表项")

    print(f"\n所有用户想看列表总数: {Watchlist.objects.count()}")


if __name__ == "__main__":
    create_watchlist_data()
