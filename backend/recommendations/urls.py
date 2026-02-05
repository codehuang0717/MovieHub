from django.urls import path
from . import views

urlpatterns = [
    path("", views.RecommendationListView.as_view(), name="recommendation-list"),
    path("popular/", views.PopularMoviesView, name="popular-movies"),
    path("trending/", views.TrendingMoviesView, name="trending-movies"),
    path(
        "personalized/",
        views.PersonalizedRecommendationsView,
        name="personalized-recommendations",
    ),
    path("similar/<int:movie_id>/", views.SimilarMoviesView, name="similar-movies"),
    path("track-activity/", views.TrackUserActivityView, name="track-activity"),
]
