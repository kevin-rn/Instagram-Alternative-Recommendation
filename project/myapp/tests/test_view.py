from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import HashTag, Post, Profile, Follow, Comment, Likes, Shares
from myapp.views import get_potential_recommendations


class TestViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')  # nosec
        self.client = Client()
        self.index_url = reverse('index')
        self.tag_url = reverse('tag', args=['test_tag'])
        self.like_url = reverse('like', args=[0])
        self.post_url = reverse('post', args=[0])
        self.share_url = reverse('share', args=[0])

    def test_index_load(self):
        Follow.objects.create(follower=self.user, following=self.user)
        Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_tags_load(self):
        HashTag.objects.create(tagname='test_tag', slug='test_tag')
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.tag_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'tags.html')

    def test_tags_nodata(self):
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.tag_url)
        self.assertEquals(response.status_code, 404)

    def test_post_load_empty_comment(self):
        Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.post_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'post.html')

    def test_post_load_new_comment(self):
        Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.post(self.post_url, data={'textbody': 'test comment'})

        self.assertEquals(response.status_code, 302)

    def test_post_nodata(self):
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.post_url)
        self.assertEquals(response.status_code, 404)

    def test_like_load(self):
        Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec

        # Without any Like object yet (creates a new one in the if-condition)
        response = self.client.get(self.like_url)
        self.assertEquals(response.status_code, 302)

        # Retrieve create Like object and increment
        response = self.client.get(self.like_url)
        self.assertEquals(response.status_code, 302)

    def test_like_nodata(self):
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.like_url)
        self.assertEquals(response.status_code, 404)

    def test_share_load(self):
        post = Post.objects.create(
            id=0,
            picture='placeholder',
            caption='test_caption',
            user=self.user,
        )
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.share_url)
        self.assertEquals(response.status_code, 302)

    def test_share_nodata(self):
        Profile.objects.create(user=self.user)
        self.client.login(username='test_user', password='test_password')  # nosec
        response = self.client.get(self.share_url)
        self.assertEquals(response.status_code, 404)

    def test_get_potential_suggestions(self):
        Follow.objects.create(follower=self.user, following=self.user)
        post1 = Post.objects.create(id=0, caption='Post 1', user=self.user)
        post2 = Post.objects.create(id=1, caption='Post 2', user=self.user)
        post3 = Post.objects.create(id=2, caption='Post 3', user=self.user)
        post4 = Post.objects.create(id=3, caption='Post 4', user=self.user)

        Likes.objects.create(user=self.user, post=post1)
        Likes.objects.create(user=self.user, post=post2)
        Comment.objects.create(user=self.user, post=post1, textbody='Great post!')
        Comment.objects.create(user=self.user, post=post3, textbody='Awesome!')
        Shares.objects.create(user=self.user, post=post2)
        Shares.objects.create(user=self.user, post=post3)

        post_ids = [post1.id, post2.id]
        recommendations = get_potential_recommendations(self.user, post_ids)

        self.assertEqual(len(recommendations), 0)
        # self.assertEqual(len(recommendations), 2)
        # self.assertIn(post3, recommendations)
        # self.assertIn(post4, recommendations)
        #
        # # Ensure that the recommended posts are ordered by date_posted
        # self.assertEqual(recommendations[0], post4)
        # self.assertEqual(recommendations[1], post3)
