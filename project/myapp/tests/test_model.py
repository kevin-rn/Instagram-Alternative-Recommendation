from django.test import TestCase
from django.contrib.auth.models import User
from myapp.models import (Comment, Follow, HashTag, Likes, Post, PostStream,
                          Profile, Shares, Story, StoryStream)


class TestModels(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password'
        ) # nosec

    def test_profile_creation(self):
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            profile_picture=None
        )

        self.assertEquals(str(profile), 'test_user')

    def test_hashtag_creation(self):
        tag = HashTag.objects.create(
            tagname='test_tag'
        )
        self.assertEquals(str(tag), 'test_tag')
        self.assertEquals(tag.get_absolute_url(), '/tag/test_tag')

    def test_post_creation(self):
        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        self.assertEquals(post.likes, 0)
        self.assertEquals(post.shares, 0)
        self.assertEquals(str(post), '0')
        self.assertEquals(post.get_absolute_url(), '/post/0')

    def test_post_stream_follow(self):
        user2 = User.objects.create_user(
            username='test_user2',
            password='test_password2'
        ) # nosec

        Follow.objects.create(
            follower=user2,
            following=self.user
        )

        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )

        # Created post should automatically create a PostStream object based on the Follow object created.
        stream = PostStream.objects.filter(user=user2)
        self.assertEquals(stream.count(), 1)
        self.assertEquals(stream[0].post, post)

    def test_story_stream_follow(self):
        user2 = User.objects.create_user(
            username='test_user2',
            password='test_password2'
        ) # nosec

        Follow.objects.create(
            follower=user2,
            following=self.user
        )

        story = Story.objects.create(user=self.user)
        self.assertEquals(str(story), 'test_user')
        stream = StoryStream.objects.filter(user=user2)
        self.assertEquals(stream.count(), 1)

    def test_like_post(self):
        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        self.assertEquals(post.likes, 0)

        like = Likes.objects.create(
            user=self.user,
            post=post
        )


    def test_share_post(self):
        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        self.assertEquals(post.shares, 0)

    def test_comment_post(self):
        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )

        comment = Comment.objects.create(
            post=post,
            user=self.user,
            textbody='test'
        )

        comments = Comment.objects.filter(post=post).order_by('date_posted')
        self.assertEquals(comments.count(), 1)
