"""Modules for handling the view"""
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
import pandas as pd
from .form import CommentForm
from .models import (Comment, Likes, Post, PostStream, Profile, Shares, HashTag,
                     StoryStream)
from .recommender import preprocessing_data, hybrid_recommendation


def get_potential_recommendations(user, post_ids):
    """Use recommendation system to get suggested posts"""

    post_df = pd.DataFrame(list(Post.objects.all().values('caption', 'hashtags', 'id')))
    post_df.rename(columns={'caption': 'title', 'hashtags': 'category', 'id': 'post_id'},
                   inplace=True)
    view_df = pd.DataFrame(list(PostStream.objects.filter(user=user).all()
                                .values('user_id', 'post_id', 'date')))
    view_df.rename(columns={'date': 'time_stamp'}, inplace=True)

    for idx, row in view_df.iterrows():
        likes = Likes.objects.filter(user_id=row['user_id'], post_id=row['post_id']).count()
        comment = Comment.objects.filter(user_id=row['user_id'], post_id=row['post_id']).count()
        shares = Shares.objects.filter(user_id=row['user_id'], post_id=row['post_id']).count()
        rating = 0.5 * likes + 0.4 * comment + 0.1 * shares
        view_df.at[idx, "Valuable"] = rating

    rating_post_matrix, rating_post_pivot = preprocessing_data(post_df=post_df, view_df=view_df)

    if rating_post_pivot.empty:
        recommended = Post.objects.filter(~Q(user=user)).all() \
            .exclude(id__in=post_ids).all().order_by('-date_posted')

    else:
        suggestions = hybrid_recommendation(rating_post_matrix, rating_post_pivot, adjustment=0.5)
        post_ids = suggestions['post_id'].tonumpy()
        recommended = Post.objects.filter(id__in=post_ids).all().order_by('-date_posted')

    return recommended


def index(request):
    """
    Handles the index page functionality
    """
    user = request.user
    # stories
    stories = StoryStream.objects.filter(user=user)
    # posts
    post_ids = [p.post.id for p in PostStream.objects.filter(user=user)]
    posts = Post.objects.filter(id__in=post_ids).all().order_by('-date_posted')
    # comments (perform list comprehension to get a preview of two comments per post)
    comments = [comment for post_id in posts for comment in
                Comment.objects.filter(post=post_id).all().order_by('-date_posted')[:2]]

    # likes
    likes = [like_item.post.id for like_item in Likes.objects.filter(user=user).all()]

    # Suggested posts
    recommended = get_potential_recommendations(user, post_ids)

    template = loader.get_template('index.html')

    context = {
        'posts': posts,
        'stories': stories,
        'comments': comments,
        'nr_comments': len(comments),
        'likes': likes,
        'recommended': recommended
    }

    return HttpResponse(template.render(context, request))


def tags(request, tag_slug):
    """
    Handles the Hashtag page functionality
    """
    tag = get_object_or_404(HashTag, slug=tag_slug)
    posts = Post.objects.filter(hashtags=tag).order_by('-date_posted')

    template = loader.get_template('tags.html')

    context = {
        'posts': posts,
        'tag': tag,
    }

    return HttpResponse(template.render(context, request))


def post(request, post_id):
    """
    Handles the post details functionality
    """
    post_value = get_object_or_404(Post, id=post_id)
    user = request.user
    profile = Profile.objects.get(user=user)
    comments = Comment.objects.filter(post=post_value).order_by('date_posted')
    # likes
    likes = [like_item.post.id for like_item in Likes.objects.filter(user=user).all()]

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post_value
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post', args=[post_id]))
    else:
        form = CommentForm()

    template = loader.get_template('post.html')

    context = {
        'post': post_value,
        'profile': profile,
        'form': form,
        'comments': comments,
        'nr_comments': comments.count(),
        'likes': likes,
    }

    return HttpResponse(template.render(context, request))


def like(request, post_id):
    """
    Handles the liking post functionality
    """
    user = request.user
    post_value = get_object_or_404(Post, id=post_id)
    current_likes = post_value.likes

    is_liked = Likes.objects.filter(user=user, post=post_value)

    if not is_liked:
        Likes.objects.create(user=user, post=post_value)
        current_likes += 1
    else:
        Likes.objects.filter(user=user, post=post_value).delete()
        current_likes -= 1

    post_value.likes = max(current_likes, 0)
    post_value.save()

    # return HttpResponseRedirect(reverse('postlike', args=[post_id]))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def share(request, post_id):
    """
    Handles the share post functionality
    """
    user = request.user
    post_value = get_object_or_404(Post, id=post_id)
    current_shares = post_value.shares

    is_shared = Shares.objects.filter(user=user, post=post_value)

    if not is_shared:
        Shares.objects.create(user=user, post=post_value)

    current_shares += 1

    post_value.shares = max(current_shares, 0)
    post_value.save()

    # return HttpResponseRedirect(reverse('postshare', args=[post_id]))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
