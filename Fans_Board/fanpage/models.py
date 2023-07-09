from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=50, unique=True)
    body = RichTextUploadingField()
    categories = models.ManyToManyField('Category', through='PostCategory', related_name='posts')
    post_created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Reply(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    body = models.TextField()
    reply_created = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text='category name')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class VerificationCode(models.Model):
    new_user_id = models.IntegerField()
    temp_code = models.CharField(max_length=10, help_text='temp_verification_code')
