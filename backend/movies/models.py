from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    poster = models.ImageField(upload_to="posters/", null=True, blank=True)
    poster_path = models.URLField(
        max_length=500, blank=True, null=True, help_text="TMDB poster path"
    )
    synopsis = models.TextField()
    release_date = models.DateField()
    duration = models.IntegerField(
        help_text="Duration in minutes", null=True, blank=True
    )
    categories = models.ManyToManyField(Category, related_name="movies")
    director = models.CharField(max_length=100, blank=True)
    cast = models.TextField(blank=True, help_text="Cast members separated by commas")
    language = models.CharField(max_length=50, default="English")
    country = models.CharField(max_length=50, blank=True)
    imdb_rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    vote_average = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="TMDB vote average",
    )
    tmdb_id = models.IntegerField(
        unique=True, null=True, blank=True, help_text="TMDB movie ID"
    )
    backdrop_path = models.URLField(
        max_length=500, blank=True, null=True, help_text="TMDB backdrop path"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.score for rating in ratings) / len(ratings)
        return 0
