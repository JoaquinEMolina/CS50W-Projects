
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('posts/<int:post_id>', views.update_post, name='update_post'),
    path('posts/<str:postbox>', views.postbox, name='postbox'),
    path('profile/<str:username>', views.user_profile, name='user_profile'),
    path('create_post', views.create_post, name='create_post'),
    path("register", views.register, name="register"),
    path("follow_unfollow/<str:username>", views.follow_unfollow, name='follow_unfollow'),
    path("like_unlike/<int:post_id>", views.like_unlike, name="like_unlike"),
    re_path(r'^posts/(all|following|[\w-]+)/?$', views.index, name='spa_route'),
]
