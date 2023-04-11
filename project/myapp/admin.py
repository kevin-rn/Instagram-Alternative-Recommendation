"""Module for admin interface."""
from django.contrib import admin

from .models import (Comment, Follow, HashTag, Likes, Post, PostStream,
                     Profile, Shares, Story, StoryStream)

# Register your models here.

myModels = [Post, Profile, HashTag, Follow, PostStream, Likes, Story, StoryStream, Comment, Shares]
admin.site.register(myModels)
