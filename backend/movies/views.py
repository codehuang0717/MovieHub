from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Movie
from .serializers import (
    CategorySerializer,
    MovieListSerializer,
    MovieDetailSerializer,
    MovieCreateUpdateSerializer,
)


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().annotate(movie_count=Count("movies"))
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


# Movie Views
class MovieListCreateView(generics.ListCreateAPIView):
    queryset = Movie.objects.all().prefetch_related("categories")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["categories", "language", "release_date"]
    search_fields = ["title", "original_title", "director", "cast"]
    ordering_fields = ["release_date", "imdb_rating", "title", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MovieCreateUpdateSerializer
        return MovieListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]


class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all().prefetch_related("categories", "ratings", "comments")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return MovieCreateUpdateSerializer
        return MovieDetailSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly()])
def MovieSearchView(request):
    query = request.GET.get("search", "").strip()
    if not query:
        return Response(
            {"error": "搜索关键词不能为空"}, status=status.HTTP_400_BAD_REQUEST
        )

    # 高级搜索参数
    category = request.GET.get("category")
    year_min = request.GET.get("year_min")
    year_max = request.GET.get("year_max")
    rating_min = request.GET.get("rating_min")
    language = request.GET.get("language")

    # 构建查询
    movies = Movie.objects.all()

    # 搜索关键词
    if query:
        movies = movies.filter(
            Q(title__icontains=query)
            | Q(original_title__icontains=query)
            | Q(director__icontains=query)
            | Q(cast__icontains=query)
            | Q(synopsis__icontains=query)
        )

    # 分类筛选
    if category:
        movies = movies.filter(categories__id=category)

    # 年份筛选
    if year_min:
        movies = movies.filter(release_date__year__gte=year_min)
    if year_max:
        movies = movies.filter(release_date__year__lte=year_max)

    # 评分筛选
    if rating_min:
        movies = movies.annotate(avg_rating=Avg("ratings__score")).filter(
            avg_rating__gte=float(rating_min)
        )

    # 语言筛选
    if language:
        movies = movies.filter(language__icontains=language)

    # 排序
    ordering = request.GET.get("ordering", "-created_at")
    if ordering == "relevance":
        # 按相关性排序（标题匹配优先）
        movies = movies.annotate(
            title_match=Count("id", filter=Q(title__icontains=query)),
            director_match=Count("id", filter=Q(director__icontains=query)),
        ).order_by("-title_match", "-director_match", "-imdb_rating")
    else:
        movies = movies.order_by(ordering)

    # 分页
    page_size = int(request.GET.get("page_size", 12))
    page = int(request.GET.get("page", 1))

    total = movies.count()
    start = (page - 1) * page_size
    end = start + page_size

    movies_page = movies[start:end]

    serializer = MovieListSerializer(
        movies_page, many=True, context={"request": request}
    )

    return Response(
        {
            "count": total,
            "next": f"?search={query}&page={page + 1}" if end < total else None,
            "previous": f"?search={query}&page={page - 1}" if page > 1 else None,
            "results": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly()])
def PopularMoviesView(request):
    # 获取热门电影（基于评分和观看次数）
    movies = (
        Movie.objects.annotate(
            avg_rating=Avg("ratings__score"),
            view_count=Count("ratings__user", distinct=True),
        )
        .filter(Q(avg_rating__gte=4) | Q(view_count__gte=10))
        .order_by("-avg_rating", "-view_count", "-imdb_rating")
    )

    page_size = min(int(request.GET.get("page_size", 20)), 50)
    movies = movies[:page_size]

    serializer = MovieListSerializer(movies, many=True, context={"request": request})

    return Response({"results": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly()])
def LatestMoviesView(request):
    # 获取最新电影
    days = int(request.GET.get("days", 30))
    movies = Movie.objects.filter(
        release_date__gte=timezone.now() - timezone.timedelta(days=days)
    ).order_by("-release_date")

    page_size = min(int(request.GET.get("page_size", 20)), 50)
    movies = movies[:page_size]

    serializer = MovieListSerializer(movies, many=True, context={"request": request})

    return Response({"results": serializer.data})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def SyncMovieView(request, movie_id: int):
    """同步TMDB电影到本地数据库"""
    import requests
    from decimal import Decimal

    try:
        # 从TMDB API获取电影信息
        tmdb_api_key = "2d89ddec4f8acd4c9f2036ea7321f326"
        tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": tmdb_api_key, "language": "zh-CN"}

        response = requests.get(tmdb_url, params=params)
        response.raise_for_status()
        tmdb_data = response.json()

        # 检查电影是否已存在
        movie, created = Movie.objects.get_or_create(
            tmdb_id=movie_id,
            defaults={
                "title": tmdb_data.get("title", ""),
                "original_title": tmdb_data.get("original_title", ""),
                "synopsis": tmdb_data.get("overview", ""),
                "release_date": tmdb_data.get("release_date"),
                "duration": tmdb_data.get("runtime"),
                "imdb_rating": Decimal(str(tmdb_data.get("vote_average", 0))),
                "vote_average": Decimal(str(tmdb_data.get("vote_average", 0))),
                "poster_path": f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path', '')}"
                if tmdb_data.get("poster_path")
                else None,
                "backdrop_path": f"https://image.tmdb.org/t/p/w1280{tmdb_data.get('backdrop_path', '')}"
                if tmdb_data.get("backdrop_path")
                else None,
            },
        )

        if not created:
            # 如果已存在，更新信息
            movie.title = tmdb_data.get("title", movie.title)
            movie.original_title = tmdb_data.get("original_title", movie.original_title)
            movie.synopsis = tmdb_data.get("overview", movie.synopsis)
            movie.release_date = tmdb_data.get("release_date", movie.release_date)
            movie.duration = tmdb_data.get("runtime", movie.duration)
            movie.imdb_rating = Decimal(
                str(tmdb_data.get("vote_average", movie.imdb_rating or 0))
            )
            movie.vote_average = Decimal(
                str(tmdb_data.get("vote_average", movie.vote_average or 0))
            )
            movie.poster_path = (
                f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path', '')}"
                if tmdb_data.get("poster_path")
                else movie.poster_path
            )
            movie.backdrop_path = (
                f"https://image.tmdb.org/t/p/w1280{tmdb_data.get('backdrop_path', '')}"
                if tmdb_data.get("backdrop_path")
                else movie.backdrop_path
            )
            movie.save()

        serializer = MovieDetailSerializer(movie, context={"request": request})

        return Response({"movie": serializer.data, "created": created})

    except requests.RequestException as e:
        return Response(
            {"error": f"从TMDB获取电影信息失败: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": f"同步电影失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
