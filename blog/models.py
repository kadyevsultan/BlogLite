from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="likes_on_post", blank=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class SubPost(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    post = models.ForeignKey(Post, related_name="subposts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
