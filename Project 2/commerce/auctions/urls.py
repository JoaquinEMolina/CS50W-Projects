from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("categoies/<str:category_name>", views.category, name="category"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("make_bid/<int:listing_id>", views.make_bid, name="make_bid"),
    path("make_comment/<int:listing_id>", views.make_comment, name="make_comment"),
    path("watchlist/<int:listing_id>/remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("watchlist/<int:listing_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:listing_id>/close", views.listing_close, name="listing_close")
]
