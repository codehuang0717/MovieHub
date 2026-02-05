from rest_framework import serializers
from .models import Rating, Comment, Collection, Watchlist
from movies.models import Movie
from movies.serializers import MovieListSerializer


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Rating
        fields = [
            "id",
            "user",
            "movie",
            "movie_title",
            "score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("评分必须在1-5之间")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        movie = attrs["movie"]

        # 检查是否已经评分
        if Rating.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError("您已经给这部电影评分过了")

        return attrs


class RatingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["score"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("评分必须在1-5之间")
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_avatar = serializers.SerializerMethodField()
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_avatar",
            "movie",
            "movie_title",
            "content",
            "is_long_review",
            "likes_count",
            "user_liked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "user_avatar",
            "likes_count",
            "user_liked",
            "created_at",
            "updated_at",
        ]

    def get_likes_count(self, obj):
        return obj.get_like_count()

    def get_user_avatar(self, obj):
        avatar = getattr(getattr(obj.user, "profile", None), "avatar", None)
        if not avatar:
            return None
        try:
            url = avatar.url
        except ValueError:
            return None

        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_user_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def validate_content(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("评论内容至少5个字符")
        if len(value) > 2000:
            raise serializers.ValidationError("评论内容不能超过2000个字符")
        return value


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "is_long_review"]

    def validate_content(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("评论内容至少5个字符")
        if len(value) > 2000:
            raise serializers.ValidationError("评论内容不能超过2000个字符")
        return value


class CollectionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movies = MovieListSerializer(many=True, read_only=True)
    movie_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "user",
            "name",
            "description",
            "movies",
            "movie_ids",
            "is_public",
            "movies_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_movies_count(self, obj):
        return obj.movies.count()

    def validate_name(self, value):
        user = self.context["request"].user
        # 检查同名收藏夹
        collection_qs = Collection.objects.filter(user=user, name=value)
        if self.instance:
            collection_qs = collection_qs.exclude(id=self.instance.id)

        if collection_qs.exists():
            raise serializers.ValidationError("您已经有同名的收藏夹了")

        return value

    def create(self, validated_data):
        movie_ids = validated_data.pop("movie_ids", [])
        collection = Collection.objects.create(**validated_data)

        if movie_ids:
            movies = Movie.objects.filter(id__in=movie_ids)
            collection.movies.set(movies)

        return collection

    def update(self, instance, validated_data):
        movie_ids = validated_data.pop("movie_ids", None)

        # 更新收藏夹信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新电影列表
        if movie_ids is not None:
            movies = Movie.objects.filter(id__in=movie_ids)
            instance.movies.set(movies)

        return instance


class WatchlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), required=False, allow_null=True
    )
    movie_info = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = [
            "id",
            "user",
            "movie",
            "tmdb_movie_id",
            "movie_title",
            "movie_poster",
            "movie_info",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_movie_info(self, obj):
        """获取电影信息，优先本地movie，然后是TMDB缓存数据"""
        if obj.movie:
            # 如果有本地movie关联，使用MovieListSerializer
            return MovieListSerializer(obj.movie, context=self.context).data

        # 如果没有本地movie，但有tmdb_movie_id，从TMDB获取基本信息
        if obj.tmdb_movie_id:
            import requests
            from decimal import Decimal

            try:
                # 从TMDB API获取电影信息
                tmdb_api_key = "2d89ddec4f8acd4c9f2036ea7321f326"
                tmdb_url = f"https://api.themoviedb.org/3/movie/{obj.tmdb_movie_id}"
                params = {"api_key": tmdb_api_key, "language": "zh-CN"}

                response = requests.get(tmdb_url, params=params, timeout=5)
                response.raise_for_status()
                tmdb_data = response.json()

                return {
                    "id": obj.tmdb_movie_id,
                    "title": obj.movie_title or tmdb_data.get("title", "未知电影"),
                    "poster_path": obj.movie_poster
                    or (
                        f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path', '')}"
                        if tmdb_data.get("poster_path")
                        else None
                    ),
                    "release_date": tmdb_data.get("release_date"),
                    "vote_average": tmdb_data.get("vote_average"),
                    "genres": tmdb_data.get("genres", []),
                }
            except (requests.RequestException, requests.Timeout):
                # 如果TMDB API失败，返回基本信息
                return {
                    "id": obj.tmdb_movie_id,
                    "title": obj.movie_title or "未知电影",
                    "poster_path": obj.movie_poster,
                    "release_date": None,
                    "vote_average": None,
                    "genres": [],
                }

        return None

    def validate(self, attrs):
        # 确保至少有一个电影引用
        movie = attrs.get("movie")
        tmdb_movie_id = attrs.get("tmdb_movie_id")

        if not movie and not tmdb_movie_id:
            raise serializers.ValidationError("必须指定电影或TMDB电影ID")

        return attrs


class WatchlistUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ["status"]

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Watchlist.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("无效的状态")
        return value
