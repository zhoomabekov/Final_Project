from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=50, unique=True)
    body = models.TextField()
    categories = models.ManyToManyField('Category', through='PostCategory', related_name='posts')


class Reply(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    body = models.TextField()


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text='category name')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
