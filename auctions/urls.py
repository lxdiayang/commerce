from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>", views.listing_view, name="listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_view, name="category"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist/remove/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("<int:listing_id>/bid", views.make_bid, name="make_bid"),
    path("<int:listing_id>/comment", views.comment, name="comment"),
    path("<int:listing_id>/close", views.close_listing, name="close_listing")
]
