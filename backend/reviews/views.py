from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Rating, Comment, Collection, Watchlist
from movies.models import Movie, Category
from .serializers import (
    RatingSerializer,
    RatingUpdateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    CollectionSerializer,
    WatchlistSerializer,
    WatchlistUpdateSerializer,
)


# Rating Views
class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["score", "movie"]
    ordering_fields = ["created_at", "score"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Rating.objects.filter(user=self.request.user)
        tmdb_movie_id = self.request.query_params.get("tmdb_movie_id")
        if tmdb_movie_id:
            movie = Movie.objects.filter(tmdb_id=tmdb_movie_id).first()
            if movie:
                queryset = queryset.filter(movie=movie)
            else:
                queryset = queryset.none()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        tmdb_movie_id = data.pop("tmdb_movie_id", None)

        if tmdb_movie_id and not data.get("movie"):
            movie = _get_or_sync_movie_by_tmdb_id(int(tmdb_movie_id))
            if not movie:
                return Response(
                    {"error": "无法同步TMDB电影"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data["movie"] = movie.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return RatingUpdateSerializer
        return RatingSerializer


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def MovieRatingsView(request, movie_id):
    """获取某部电影的所有评分"""
    movie = _get_movie_by_id_or_tmdb(movie_id)
    if not movie:
        return Response(
            {
                "stats": {
                    "total_ratings": 0,
                    "average_rating": None,
                    "rating_1": 0,
                    "rating_2": 0,
                    "rating_3": 0,
                    "rating_4": 0,
                    "rating_5": 0,
                },
                "ratings": [],
            }
        )

    ratings = Rating.objects.filter(movie=movie).select_related("user")

    # 统计信息
    rating_stats = ratings.aggregate(
        total_ratings=Count("id"),
        average_rating=Avg("score"),
        rating_1=Count("id", filter=Q(score=1)),
        rating_2=Count("id", filter=Q(score=2)),
        rating_3=Count("id", filter=Q(score=3)),
        rating_4=Count("id", filter=Q(score=4)),
        rating_5=Count("id", filter=Q(score=5)),
    )

    serializer = RatingSerializer(ratings, many=True)

    return Response({"stats": rating_stats, "ratings": serializer.data})


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["movie", "is_long_review", "user"]
    ordering_fields = ["created_at", "likes_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Comment.objects.select_related("user", "movie")
        movie_id = self.request.query_params.get("movie")
        tmdb_movie_id = self.request.query_params.get("tmdb_movie_id")
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        elif tmdb_movie_id:
            movie = Movie.objects.filter(tmdb_id=tmdb_movie_id).first()
            if movie:
                queryset = queryset.filter(movie=movie)
            else:
                queryset = queryset.none()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        tmdb_movie_id = data.pop("tmdb_movie_id", None)

        if tmdb_movie_id and not data.get("movie"):
            movie = _get_or_sync_movie_by_tmdb_id(int(tmdb_movie_id))
            if not movie:
                return Response(
                    {"error": "无法同步TMDB电影"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data["movie"] = movie.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CommentUpdateSerializer
        return CommentSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def CommentLikeView(request, pk):
    """点赞/取消点赞评论"""
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response({"error": "评论不存在"}, status=status.HTTP_404_NOT_FOUND)

    if comment.likes.filter(id=request.user.id).exists():
        # 取消点赞
        comment.likes.remove(request.user)
        return Response({"liked": False, "likes_count": comment.get_like_count()})
    else:
        # 点赞
        comment.likes.add(request.user)
        return Response({"liked": True, "likes_count": comment.get_like_count()})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def MovieCommentsView(request, movie_id):
    """获取某部电影的所有评论"""
    movie = _get_movie_by_id_or_tmdb(movie_id)
    if not movie:
        return Response({"count": 0, "results": []})

    comments = Comment.objects.filter(movie=movie).select_related("user")

    # 筛选参数
    is_long_review = request.query_params.get("is_long_review")
    if is_long_review is not None:
        comments = comments.filter(is_long_review=is_long_review.lower() == "true")

    serializer = CommentSerializer(comments, many=True, context={"request": request})

    return Response({"count": comments.count(), "results": serializer.data})


# Collection Views
class CollectionListCreateView(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["is_public"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.request.query_params.get("public"):
            # 查看公开的收藏夹
            return Collection.objects.filter(is_public=True)
        return Collection.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get("public"):
            return Collection.objects.filter(is_public=True)
        return Collection.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def AddMovieToCollectionView(request, collection_id, movie_id):
    """将电影添加到收藏夹"""
    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        movie = _get_movie_by_id_or_tmdb(movie_id)
        if not movie:
            movie = _get_or_sync_movie_by_tmdb_id(movie_id)
    except Collection.DoesNotExist:
        return Response(
            {"error": "收藏夹或电影不存在"}, status=status.HTTP_404_NOT_FOUND
        )

    if not movie:
        return Response(
            {"error": "收藏夹或电影不存在"}, status=status.HTTP_404_NOT_FOUND
        )

    if collection.movies.filter(id=movie_id).exists():
        return Response(
            {"error": "电影已在收藏夹中"}, status=status.HTTP_400_BAD_REQUEST
        )

    collection.movies.add(movie)
    return Response({"message": "添加成功"})


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def RemoveMovieFromCollectionView(request, collection_id, movie_id):
    """从收藏夹移除电影"""
    try:
        collection = Collection.objects.get(id=collection_id, user=request.user)
        movie = _get_movie_by_id_or_tmdb(movie_id)
    except Collection.DoesNotExist:
        return Response(
            {"error": "收藏夹或电影不存在"}, status=status.HTTP_404_NOT_FOUND
        )

    if not movie:
        return Response(
            {"error": "收藏夹或电影不存在"}, status=status.HTTP_404_NOT_FOUND
        )

    if not collection.movies.filter(id=movie_id).exists():
        return Response(
            {"error": "电影不在收藏夹中"}, status=status.HTTP_400_BAD_REQUEST
        )

    collection.movies.remove(movie)
    return Response({"message": "移除成功"})


# Watchlist Views
class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "movie", "tmdb_movie_id"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related("movie")


class WatchlistDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related(
            "movie"
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return WatchlistUpdateSerializer
        return WatchlistSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def ToggleWatchlistView(request, movie_id):
    """切换电影在想看列表中的状态"""
    import requests

    movie = None
    movie_title = ""
    movie_poster = None

    # 首先尝试通过tmdb_id查找电影
    try:
        movie = Movie.objects.get(tmdb_id=movie_id)
    except Movie.DoesNotExist:
        pass

    # 如果通过tmdb_id没找到，尝试通过id查找
    if not movie:
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            pass

    # 如果电影不存在，从TMDB获取基本信息
    if not movie:
        try:
            # 从TMDB API获取电影基本信息
            tmdb_api_key = "2d89ddec4f8acd4c9f2036ea7321f326"
            tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {"api_key": tmdb_api_key, "language": "zh-CN"}

            response = requests.get(tmdb_url, params=params)
            response.raise_for_status()
            tmdb_data = response.json()

            movie_title = tmdb_data.get("title", "")
            if tmdb_data.get("poster_path"):
                movie_poster = (
                    f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path')}"
                )

        except requests.RequestException as e:
            return Response(
                {"error": f"从TMDB获取电影信息失败: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # 检查是否已存在想看列表项
    try:
        if movie:
            watchlist_item = Watchlist.objects.get(user=request.user, movie=movie)
        else:
            watchlist_item = Watchlist.objects.get(
                user=request.user, tmdb_movie_id=movie_id
            )

        # 如果存在，删除（取消想看）
        watchlist_item.delete()
        return Response({"in_watchlist": False})

    except Watchlist.DoesNotExist:
        # 不存在，创建新的想看列表项
        if movie:
            watchlist_item = Watchlist.objects.create(
                user=request.user, movie=movie, status="want_to_watch"
            )
        else:
            watchlist_item = Watchlist.objects.create(
                user=request.user,
                tmdb_movie_id=movie_id,
                movie_title=movie_title,
                movie_poster=movie_poster,
                status="want_to_watch",
            )

        serializer = WatchlistSerializer(watchlist_item)
        return Response({"in_watchlist": True, "item": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def UserWatchlistStatsView(request):
    """获取用户想看列表统计"""
    user = request.user
    stats = Watchlist.objects.filter(user=user).aggregate(
        total=Count("id"),
        want_to_watch=Count("id", filter=Q(status="want_to_watch")),
        watching=Count("id", filter=Q(status="watching")),
        watched=Count("id", filter=Q(status="watched")),
    )

    return Response(stats)


def _get_movie_by_id_or_tmdb(movie_id: int):
    movie = Movie.objects.filter(id=movie_id).first()
    if movie:
        return movie
    return Movie.objects.filter(tmdb_id=movie_id).first()


def _get_or_sync_movie_by_tmdb_id(tmdb_id: int):
    movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
    if movie:
        return movie

    import requests
    from decimal import Decimal
    from datetime import date

    try:
        tmdb_api_key = "2d89ddec4f8acd4c9f2036ea7321f326"
        tmdb_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": tmdb_api_key, "language": "zh-CN"}

        response = requests.get(tmdb_url, params=params, timeout=8)
        response.raise_for_status()
        tmdb_data = response.json()

        release_date_value = tmdb_data.get("release_date")
        try:
            release_date = (
                date.fromisoformat(release_date_value)
                if release_date_value
                else date(1900, 1, 1)
            )
        except ValueError:
            release_date = date(1900, 1, 1)

        movie = Movie.objects.create(
            title=tmdb_data.get("title") or "未知电影",
            original_title=tmdb_data.get("original_title") or "",
            synopsis=tmdb_data.get("overview") or "暂无简介",
            release_date=release_date,
            duration=tmdb_data.get("runtime") or None,
            language=tmdb_data.get("original_language") or "Unknown",
            country=(tmdb_data.get("production_countries") or [{}])[0].get("name", ""),
            imdb_rating=Decimal(str(tmdb_data.get("vote_average", 0) or 0)),
            vote_average=Decimal(str(tmdb_data.get("vote_average", 0) or 0)),
            tmdb_id=tmdb_id,
            poster_path=(
                f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path')}"
                if tmdb_data.get("poster_path")
                else None
            ),
            backdrop_path=(
                f"https://image.tmdb.org/t/p/w1280{tmdb_data.get('backdrop_path')}"
                if tmdb_data.get("backdrop_path")
                else None
            ),
        )

        categories = []
        for genre in tmdb_data.get("genres", []):
            name = genre.get("name")
            if not name:
                continue
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": ""}
            )
            categories.append(category)

        if categories:
            movie.categories.set(categories)

        return movie
    except (requests.RequestException, requests.Timeout, ValueError):
        return None
