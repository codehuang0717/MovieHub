#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from reviews.models import Watchlist
from movies.models import Movie


def create_watchlist_data():
    print("=== Creating watchlist data ===")

    users = User.objects.all()
    movies = Movie.objects.all()

    if not users.exists():
        print("No users found!")
        return

    if not movies.exists():
        print("No movies found!")
        return

    # 为所有用户创建想看列表
    for i, user in enumerate(users):
        print(f"Creating watchlist for user: {user.username}")

        # 为每个用户添加3部电影
        for j in range(min(3, movies.count())):
            movie_index = (i * 3 + j) % movies.count()
            movie = movies[movie_index]

            if not Watchlist.objects.filter(user=user, movie=movie).exists():
                try:
                    status = ["want_to_watch", "watching", "watched"][j % 3]

                    Watchlist.objects.create(user=user, movie=movie, status=status)

                    print(f"  Added: {movie.title} ({status})")

                except Exception as e:
                    print(f"  Failed to add {movie.title}: {e}")

    # 显示统计
    print(f"\nTotal users: {users.count()}")
    print(f"Total movies: {movies.count()}")
    print(f"Total watchlist items: {Watchlist.objects.count()}")

    # 显示每个用户的想看列表
    for user in users:
        count = Watchlist.objects.filter(user=user).count()
        print(f"{user.username}: {count} items")


if __name__ == "__main__":
    create_watchlist_data()
