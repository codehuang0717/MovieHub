from rest_framework import serializers
from .models import Category, Movie


class CategorySerializer(serializers.ModelSerializer):
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "movie_count"]
        read_only_fields = ["created_at"]

    def get_movie_count(self, obj):
        return obj.movies.count()


class MovieListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    poster_path = serializers.SerializerMethodField()
    vote_average = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "poster",
            "poster_path",
            "release_date",
            "duration",
            "categories",
            "average_rating",
            "vote_average",
            "imdb_rating",
            "tmdb_id",
        ]

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_poster_path(self, obj):
        if obj.poster:
            return obj.poster.url if hasattr(obj.poster, "url") else str(obj.poster)
        # Return TMDB poster_path if available from sync
        return getattr(obj, "poster_path", None)

    def get_vote_average(self, obj):
        # Return TMDB vote_average if available, otherwise imdb_rating
        return getattr(obj, "vote_average", obj.imdb_rating)


class MovieDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    user_rating = serializers.SerializerMethodField()
    in_watchlist = serializers.SerializerMethodField()
    user_collections = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "original_title",
            "poster",
            "synopsis",
            "release_date",
            "duration",
            "categories",
            "director",
            "cast",
            "language",
            "country",
            "imdb_rating",
            "average_rating",
            "user_rating",
            "in_watchlist",
            "user_collections",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_user_rating(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            return rating.score if rating else None
        return None

    def get_in_watchlist(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from reviews.models import Watchlist

            return Watchlist.objects.filter(user=request.user, movie=obj).exists()
        return False

    def get_user_collections(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from reviews.models import Collection

            return Collection.objects.filter(user=request.user, movies=obj).values_list(
                "id", "name"
            )
        return []


class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all()
    )

    class Meta:
        model = Movie
        fields = [
            "title",
            "original_title",
            "poster",
            "synopsis",
            "release_date",
            "duration",
            "categories",
            "director",
            "cast",
            "language",
            "country",
            "imdb_rating",
        ]

    def validate_release_date(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("上映日期不能是未来日期")
        return value

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("时长必须大于0")
        return value

    def validate_imdb_rating(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("IMDb评分必须在0-10之间")
        return value
