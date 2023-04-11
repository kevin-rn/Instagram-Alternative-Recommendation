from django.test import SimpleTestCase
from myapp.form import CommentForm
class TestForms(SimpleTestCase):

    def test_comment_form_valid(self):
        form = CommentForm(data={
         'textbody': 'Test Comment'
        })
        self.assertTrue(form.is_valid())

    def test_comment_form_empty(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
