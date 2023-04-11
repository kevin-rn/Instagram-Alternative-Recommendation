from django.test import SimpleTestCase
from django.urls import reverse, resolve
from myapp.views import index, like, post, share, tags


class TestUrls(SimpleTestCase):
    def test_url_index_resolve(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_url_tag_resolve(self):
        url = reverse('tag', args=['test-slug'])
        self.assertEquals(resolve(url).func, tags)

    def test_url_like_resolve(self):
        url = reverse('like', args=[0])
        self.assertEquals(resolve(url).func, like)

    def test_url_post_resolve(self):
        url = reverse('post', args=[0])
        self.assertEquals(resolve(url).func, post)

    def test_url_share_resolve(self):
        url = reverse('share', args=[0])
        self.assertEquals(resolve(url).func, share)
