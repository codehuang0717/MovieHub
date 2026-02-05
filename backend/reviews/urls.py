from django.urls import path
from . import views

urlpatterns = [
    # Ratings
    path("ratings/", views.RatingListCreateView.as_view(), name="rating-list-create"),
    path("ratings/<int:pk>/", views.RatingDetailView.as_view(), name="rating-detail"),
    path(
        "movies/<int:movie_id>/ratings/", views.MovieRatingsView, name="movie-ratings"
    ),
    # Comments
    path(
        "comments/", views.CommentListCreateView.as_view(), name="comment-list-create"
    ),
    path(
        "comments/<int:pk>/", views.CommentDetailView.as_view(), name="comment-detail"
    ),
    path("comments/<int:pk>/like/", views.CommentLikeView, name="comment-like"),
    path(
        "movies/<int:movie_id>/comments/",
        views.MovieCommentsView,
        name="movie-comments",
    ),
    # Collections
    path(
        "collections/",
        views.CollectionListCreateView.as_view(),
        name="collection-list-create",
    ),
    path(
        "collections/<int:pk>/",
        views.CollectionDetailView.as_view(),
        name="collection-detail",
    ),
    path(
        "collections/<int:collection_id>/movies/<int:movie_id>/",
        views.AddMovieToCollectionView,
        name="add-movie-to-collection",
    ),
    path(
        "collections/<int:collection_id>/movies/<int:movie_id>/remove/",
        views.RemoveMovieFromCollectionView,
        name="remove-movie-from-collection",
    ),
    # Watchlist
    path(
        "watchlist/",
        views.WatchlistListCreateView.as_view(),
        name="watchlist-list-create",
    ),
    path(
        "watchlist/<int:pk>/",
        views.WatchlistDetailView.as_view(),
        name="watchlist-detail",
    ),
    path(
        "watchlist/toggle/<int:movie_id>/",
        views.ToggleWatchlistView,
        name="toggle-watchlist",
    ),
    path("watchlist/stats/", views.UserWatchlistStatsView, name="watchlist-stats"),
]
