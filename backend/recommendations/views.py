from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from .models import Recommendation, UserActivity
from movies.models import Movie


class RecommendationListView(generics.ListAPIView):
    """获取推荐电影列表"""

    serializer_class = None  # 使用MovieListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Movie.objects.none()  # 这里会重写get方法

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.is_authenticated:
            # 已登录用户 - 个性化推荐
            recommendations = (
                Recommendation.objects.filter(user=user)
                .select_related("movie")
                .order_by("-score")[:20]
            )

            movies = [rec.movie for rec in recommendations]
            from movies.serializers import MovieListSerializer

            serializer = MovieListSerializer(movies, many=True)

            return Response({"type": "personalized", "results": serializer.data})
        else:
            # 匿名用户 - 热门推荐
            popular_movies = (
                Movie.objects.annotate(
                    avg_rating=Avg("ratings__score"), rating_count=Count("ratings")
                )
                .filter(avg_rating__gte=4, rating_count__gte=5)
                .order_by("-avg_rating", "-rating_count")[:20]
            )

            from movies.serializers import MovieListSerializer

            serializer = MovieListSerializer(popular_movies, many=True)

            return Response({"type": "popular", "results": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def PopularMoviesView(request):
    """获取热门电影"""
    # 基于评分和观看次数的热门电影
    movies = (
        Movie.objects.annotate(
            avg_rating=Avg("ratings__score"),
            rating_count=Count("ratings"),
            watchlist_count=Count("watched_by", distinct=True),
        )
        .filter(Q(avg_rating__gte=4) | Q(watchlist_count__gte=10))
        .order_by("-avg_rating", "-watchlist_count", "-rating_count")[:30]
    )

    from movies.serializers import MovieListSerializer

    serializer = MovieListSerializer(movies, many=True)

    return Response({"results": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def TrendingMoviesView(request):
    """获取趋势电影（最近热门）"""
    days = int(request.GET.get("days", 7))
    since_date = timezone.now() - timezone.timedelta(days=days)

    # 基于最近活动和评分的趋势电影
    movies = (
        Movie.objects.annotate(
            recent_ratings=Count(
                "ratings", filter=Q(ratings__created_at__gte=since_date)
            ),
            recent_watchlist=Count(
                "watched_by", filter=Q(watched_by__created_at__gte=since_date)
            ),
            avg_rating=Avg("ratings__score"),
        )
        .filter(Q(recent_ratings__gte=3) | Q(recent_watchlist__gte=5))
        .order_by("-recent_ratings", "-recent_watchlist", "-avg_rating")[:30]
    )

    from movies.serializers import MovieListSerializer

    serializer = MovieListSerializer(movies, many=True)

    return Response({"days": days, "results": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def PersonalizedRecommendationsView(request):
    """获取个性化推荐"""
    user = request.user

    # 基于用户观看历史的推荐
    watched_movies = Movie.objects.filter(
        Q(ratings__user=user) | Q(watched_by__user=user)
    ).distinct()

    if not watched_movies.exists():
        # 新用户推荐最新和热门电影
        return Response(
            {
                "type": "new_user",
                "message": "欢迎新用户！为您推荐最新和热门电影",
                "results": [],
            }
        )

    # 分析用户偏好
    user_categories = (
        watched_movies.values("categories")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # 推荐相似分类的高评分电影
    category_ids = [item["categories"] for item in user_categories]
    recommended_movies = (
        Movie.objects.filter(categories__id__in=category_ids)
        .exclude(Q(ratings__user=user) | Q(watched_by__user=user))
        .annotate(avg_rating=Avg("ratings__score"), rating_count=Count("ratings"))
        .filter(avg_rating__gte=4)
        .order_by("-avg_rating", "-rating_count")[:20]
    )

    from movies.serializers import MovieListSerializer

    serializer = MovieListSerializer(recommended_movies, many=True)

    return Response(
        {
            "type": "personalized",
            "based_on_categories": user_categories,
            "results": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def SimilarMoviesView(request, movie_id):
    """获取相似电影推荐"""
    try:
        target_movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "电影不存在"}, status=404)

    # 基于分类、导演、演员的相似度推荐
    similar_movies = (
        Movie.objects.filter(
            Q(categories__in=target_movie.categories.all())
            | Q(director__icontains=target_movie.director)
            if target_movie.director
            else Q()
        )
        .exclude(id=movie_id)
        .annotate(
            category_match=Count(
                "categories", filter=Q(categories__in=target_movie.categories.all())
            ),
            avg_rating=Avg("ratings__score"),
        )
        .filter(category_match__gte=1)
        .order_by("-category_match", "-avg_rating")[:15]
    )

    from movies.serializers import MovieListSerializer

    serializer = MovieListSerializer(similar_movies, many=True)

    return Response(
        {
            "target_movie": {"id": target_movie.id, "title": target_movie.title},
            "results": serializer.data,
        }
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def TrackUserActivityView(request):
    """记录用户活动"""
    movie_id = request.data.get("movie_id")
    activity_type = request.data.get("activity_type")
    metadata = request.data.get("metadata", {})

    if not movie_id or not activity_type:
        return Response({"error": "缺少必需参数"}, status=400)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "电影不存在"}, status=404)

    # 记录活动
    activity = UserActivity.objects.create(
        user=request.user, movie=movie, activity_type=activity_type, metadata=metadata
    )

    # 异步生成推荐（简化版本，实际应用中可以用Celery）
    if activity_type in ["rate", "comment"]:
        generate_recommendations_for_user(request.user)

    return Response({"message": "活动已记录", "activity_id": activity.id})


def generate_recommendations_for_user(user):
    """为用户生成推荐（简化版本）"""
    # 清除旧推荐
    Recommendation.objects.filter(user=user).delete()

    # 获取用户喜欢的电影（评分4星以上）
    liked_movies = Movie.objects.filter(ratings__user=user, ratings__score__gte=4)

    if not liked_movies.exists():
        return

    # 获取用户偏好的分类
    liked_categories = (
        liked_movies.values("categories")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # 为每个分类推荐电影
    for category_data in liked_categories:
        category_id = category_data["categories"]
        count = category_data["count"]

        # 查找该分类的高评分电影，排除用户已看过的
        recommended_movies = (
            Movie.objects.filter(categories__id=category_id)
            .exclude(Q(ratings__user=user) | Q(watched_by__user=user))
            .annotate(avg_rating=Avg("ratings__score"))
            .filter(avg_rating__gte=4)
            .order_by("-avg_rating")[:5]
        )

        # 创建推荐记录
        for movie in recommended_movies:
            Recommendation.objects.create(
                user=user,
                movie=movie,
                recommendation_type="personalized",
                score=5.0 * (count / liked_movies.count()),  # 基于分类偏好计算分数
                reason=f"基于您对{count}部{Movie.categories.through.objects.filter(movie__in=liked_movies, category_id=category_id).first().category.name}类电影的喜好推荐",
            )
