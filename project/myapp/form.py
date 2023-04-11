"""Modules for handling Comment forms"""
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """Comment Form class"""

    textbody = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea'}), required=True)

    class Meta:
        """Meta class"""

        model = Comment
        fields = ('textbody',)
