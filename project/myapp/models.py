"""Modules for handling the database models"""
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.urls import reverse
from django.utils.text import slugify


def user_dir_path(instance, filename):  # pragma: no cover
    """Helper function for storing files of the users"""

    picture_name = f'user_{instance.user.id}/{filename}'

    full_path = os.path.join(settings.MEDIA_ROOT, picture_name)
    if os.path.exists(full_path):
        os.remove(full_path)

    return picture_name


class Profile(models.Model):
    """Profile model"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_dir_path, blank=True, null=True,
                                        verbose_name='profile_picture')

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    """Follow model"""

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')


class HashTag(models.Model):
    """Hashtag model"""

    tagname = models.CharField(max_length=75, verbose_name='Hashtag')
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        """Meta class"""
        verbose_name_plural = 'Hashtags'

    def get_absolute_url(self):
        """returns absolute url for hashtag"""
        return reverse('tag', args=[self.slug])

    def __str__(self):
        """Returns hastag name"""
        return self.tagname

    def save(self, *args, **kwargs):
        """Saves hashtag object"""
        if not self.slug:
            self.slug = slugify(self.tagname)
        return super().save(*args, **kwargs)


class Post(models.Model):
    """Post model"""

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.IntegerField(primary_key=True, default=0)
    picture = models.ImageField(upload_to=user_dir_path, verbose_name='Post', null=False)
    caption = models.CharField(max_length=2200, verbose_name='Caption')
    date_posted = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(HashTag, related_name='Hashtag')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    def get_absolute_url(self):
        """Returns absolute url for the post"""
        return reverse('post', args=[str(self.id)])

    def __str__(self):
        """returns post id"""
        return str(self.id)


class PostStream(models.Model):
    """Post stream model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        """Adds post for every follower"""
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)  # get all following
        for fol in followers:
            stream = PostStream(user=fol.follower, following=user, post=post, date=post.date_posted)
            stream.save()


class Likes(models.Model):
    """Like model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    def like_post(sender, instance, *args, **kwargs):
        """like post functionality"""
        like = instance
        post = like.post
        sender = like.user

    def unlike_post(sender, instance, *args, **kwargs):
        """unlike post functionality"""
        like = instance
        post = like.post
        sender = like.user


class Shares(models.Model):
    """Share model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_share')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_share')

    def share_post(sender, instance, *args, **kwargs):
        """share post functionality"""
        share = instance
        post = share.post
        sender = share.user


class Comment(models.Model):
    """Comment model"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    textbody = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def user_comment_post(sender, instance, *args, **kwargs):
        """User add comment functionality"""
        comment = instance
        post = comment.post
        text_preview = comment.textbody[:90]
        sender = comment.user

    def user_del_comment_post(sender, instance, *args, **kwargs):
        """User delete comment functionality"""
        comment = instance
        post = comment.post
        sender = comment.user


class Story(models.Model):
    """Story model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_user')

    def __str__(self):
        """returns name of the user of story"""
        return self.user.username


class StoryStream(models.Model):
    """Story stream model"""

    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ManyToManyField(Story, related_name='story_stream')

    def add_post(sender, instance, *args, **kwargs):
        """Adds stream for every follower"""
        story = instance
        user = story.user
        followers = Follow.objects.all().filter(following=user)

        for follower in followers:
            try:
                stream = StoryStream.objects.get(user=follower.follower, following=user)
            except StoryStream.DoesNotExist:
                stream = StoryStream.objects.create(user=follower.follower, following=user)
            stream.story.add(story)
            stream.save()


# Automatically send stream to the followers whenever a Post, Story or Comment is created
post_save.connect(PostStream.add_post, sender=Post)
post_save.connect(StoryStream.add_post, sender=Story)
post_save.connect(Comment.user_comment_post, sender=Comment)
post_save.connect(Likes.like_post, sender=Likes)
post_delete.connect(Likes.unlike_post, sender=Likes)
post_save.connect(Shares.share_post, sender=Shares)
