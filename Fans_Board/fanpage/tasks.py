from datetime import timedelta

from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.conf import settings
from .models import Post, CustomUser
from django.utils import timezone


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


# @shared_task
# def new_post_notification(post_id):
#     post = Post.objects.get(id=post_id)
#     categories = post.categories.all()
#
#     for category in categories:
#         subscribers = category.subscribers.all()
#         recipient_list = [subscriber.user.email for subscriber in subscribers]
#
#         # subject = f"New {post.get_type_display()} posted in category {category.name}: {post.title}"
#         # message = f"Dear User,\n\nA new {post.get_type_display()} has been posted in the category '{category.name}' on our site with the title: {post.title}.\n\nYou can read it here: {post.get_absolute_url()}"
#         # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
#
#         html_content = render_to_string(
#             'new_post_email_to_subscribers.html',
#             {
#                 'post': post,
#                 'category': category,
#             }
#         )
#
#         msg = EmailMultiAlternatives(
#             subject=f'Новая статья в категории "{category.name}"',
#             body='К сожалению, возникли проблемы с рендерингом HTML',
#             # Body текст будет выслан, если не сработает HTML версия
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=recipient_list,
#         )
#         msg.attach_alternative(html_content, "text/html")  # добавляем html
#
#         msg.send()  # отсылаем


@shared_task
def weekly_notification():
    all_users = CustomUser.objects.all()
    seven_days_ago = timezone.now() - timedelta(days=7)

    for user in all_users:
        posts = Post.objects.filter(post_created__gte=seven_days_ago)

        html_content = render_to_string(
            'weekly_notifier.html',
            {
                'posts': posts,
                'username': user.username,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Дайджест постов за прошедшую неделю',
            body='К сожалению, возникли проблемы с рендерингом HTML',
            # Body текст будет выслан, если не сработает HTML версия
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем
