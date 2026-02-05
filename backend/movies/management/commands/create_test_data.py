# 创建一些测试数据的管理命令

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Category, Movie
from reviews.models import Rating, Comment, Collection, Watchlist
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "创建测试数据"

    def handle(self, *args, **options):
        # 创建分类
        categories_data = [
            {"name": "动作", "description": "充满刺激和冒险的电影"},
            {"name": "喜剧", "description": "让人开怀大笑的轻松电影"},
            {"name": "科幻", "description": "探索未来和科技的奇幻世界"},
            {"name": "爱情", "description": "讲述爱情故事的浪漫电影"},
            {"name": "惊悚", "description": "紧张刺激的悬疑电影"},
            {"name": "动画", "description": "适合全家观看的动画电影"},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"description": cat_data["description"]}
            )
            categories.append(category)
            if created:
                self.stdout.write(f"创建分类: {category.name}")

        # 创建电影
        movies_data = [
            {
                "title": "复仇者联盟4：终局之战",
                "original_title": "Avengers: Endgame",
                "synopsis": "超级英雄们为了拯救宇宙，与灭霸展开最终决战。",
                "release_date": "2019-04-24",
                "duration": 181,
                "director": "罗素兄弟",
                "cast": "小罗伯特·唐尼, 克里斯·埃文斯, 马克·鲁弗洛",
                "language": "English",
                "country": "USA",
                "imdb_rating": 8.4,
                "categories": [categories[0], categories[2]],  # 动作, 科幻
            },
            {
                "title": "泰坦尼克号",
                "original_title": "Titanic",
                "synopsis": "1912年，豪华客轮泰坦尼克号与冰山相撞，一段跨越阶级的爱情故事。",
                "release_date": "1997-12-19",
                "duration": 194,
                "director": "詹姆斯·卡梅隆",
                "cast": "莱昂纳多·迪卡普里奥, 凯特·温斯莱特",
                "language": "English",
                "country": "USA",
                "imdb_rating": 7.8,
                "categories": [categories[3]],  # 爱情
            },
            {
                "title": "千与千寻",
                "original_title": "千と千尋の神隠し",
                "synopsis": "10岁少女千寻意外来到神灵世界，为了拯救父母展开冒险。",
                "release_date": "2001-07-20",
                "duration": 125,
                "director": "宫崎骏",
                "cast": "柊瑠美, 入野自由",
                "language": "Japanese",
                "country": "Japan",
                "imdb_rating": 8.6,
                "categories": [categories[5]],  # 动画
            },
            {
                "title": "盗梦空间",
                "original_title": "Inception",
                "synopsis": "擅长潜入他人梦境盗取机密的主角，接受了一项看似不可能的任务。",
                "release_date": "2010-09-01",
                "duration": 148,
                "director": "克里斯托弗·诺兰",
                "cast": "莱昂纳多·迪卡普里奥, 玛丽昂·歌迪亚",
                "language": "English",
                "country": "USA",
                "imdb_rating": 8.8,
                "categories": [categories[2], categories[4]],  # 科幻, 惊悚
            },
            {
                "title": "美人鱼",
                "original_title": "The Mermaid",
                "synopsis": "人类商人爱上了神秘的美人鱼，面临爱情与责任的选择。",
                "release_date": "2016-02-08",
                "duration": 94,
                "director": "周星驰",
                "cast": "邓超, 罗志祥, 张雨绮",
                "language": "Chinese",
                "country": "China",
                "imdb_rating": 6.3,
                "categories": [categories[1], categories[3]],  # 喜剧, 爱情
            },
        ]

        movies = []
        for movie_data in movies_data:
            categories = movie_data.pop("categories")
            movie, created = Movie.objects.get_or_create(
                title=movie_data["title"], defaults=movie_data
            )
            if created:
                movie.categories.set(categories)
                self.stdout.write(f"创建电影: {movie.title}")
            movies.append(movie)

        self.stdout.write(self.style.SUCCESS("测试数据创建完成！"))
