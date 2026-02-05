from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie


class Recommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ("popular", "Popular"),
        ("trending", "Trending"),
        ("personalized", "Personalized"),
        ("similar", "Similar Movies"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendations",
        null=True,
        blank=True,
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="recommendations"
    )
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Recommendation confidence score"
    )
    reason = models.TextField(blank=True, help_text="Why this movie is recommended")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "recommendation_type"]),
            models.Index(fields=["recommendation_type", "score"]),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.movie.title} ({self.recommendation_type})"
        return f"{self.movie.title} ({self.recommendation_type})"


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ("view", "Viewed"),
        ("search", "Searched"),
        ("rate", "Rated"),
        ("comment", "Commented"),
        ("add_to_watchlist", "Added to Watchlist"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="user_activities"
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    metadata = models.JSONField(
        null=True, blank=True, help_text="Additional activity data"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "activity_type"]),
            models.Index(fields=["activity_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.movie.title}"
