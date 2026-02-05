from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie


class Rating(models.Model):
    SCORE_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.score} stars"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    is_long_review = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.content[:50]}"

    def get_like_count(self):
        return self.likes.count()


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField(Movie, related_name="collections", blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Watchlist(models.Model):
    STATUS_CHOICES = [
        ("want_to_watch", "Want to Watch"),
        ("watching", "Currently Watching"),
        ("watched", "Watched"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="watched_by",
        null=True,
        blank=True,
    )
    tmdb_movie_id = models.IntegerField(
        null=True, blank=True, help_text="TMDB movie ID for movies not in local DB"
    )
    movie_title = models.CharField(
        max_length=200, blank=True, help_text="Movie title cache"
    )
    movie_poster = models.URLField(
        max_length=500, blank=True, null=True, help_text="Movie poster URL cache"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="want_to_watch",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"],
                name="unique_user_movie_watchlist",
                condition=models.Q(movie__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "tmdb_movie_id"],
                name="unique_user_tmdb_movie_watchlist",
                condition=models.Q(tmdb_movie_id__isnull=False),
            ),
        ]

    def __str__(self):
        title = self.get_movie_title()
        return f"{self.user.username} - {title} - {self.status}"

    def get_movie_title(self):
        if self.movie:
            return self.movie.title
        elif self.movie_title:
            return self.movie_title
        elif self.tmdb_movie_id:
            return f"TMDB Movie {self.tmdb_movie_id}"
        return "Unknown Movie"
