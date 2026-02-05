from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<int:pk>/",
        views.CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # Movies
    path("", views.MovieListCreateView.as_view(), name="movie-list-create"),
    path("<int:pk>/", views.MovieDetailView.as_view(), name="movie-detail"),
    path("search/", views.MovieSearchView, name="movie-search"),
    path("popular/", views.PopularMoviesView, name="popular-movies"),
    path("latest/", views.LatestMoviesView, name="latest-movies"),
    path("sync/<int:movie_id>/", views.SyncMovieView, name="sync-movie"),
]
