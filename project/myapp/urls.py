"""Module for handling url paths"""
from django.urls import path

from .views import index, like, post, share, tags

urlpatterns = [
    path('', index, name='index'),
    path('tag/<slug:tag_slug>', tags, name='tag'),
    path('post/<int:post_id>', post, name='post'),
    path('like/<int:post_id>', like, name='like'),
    path('share/<int:post_id>', share, name='share')
]
