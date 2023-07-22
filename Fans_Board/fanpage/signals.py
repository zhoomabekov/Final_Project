from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reply
from dotenv import load_dotenv
import os

load_dotenv()
MY_EMAIL = os.getenv('MY_EMAIL')


@receiver(post_save, sender=Reply)
def new_reply_notification(sender,instance, created, **kwargs):
    if created:
        post_title = instance.post.title
        body = instance.body
        author_email = instance.post.author.email
        author_name = instance.post.author.username

        # Оповещение об отклике
        subject = f'Новый отклик на пост'
        message = f'''
        Ваш пост под названием "{post_title}" получил отклик:
        {body}
        
        Автор отклика: {instance.author}
        '''
        from_email = MY_EMAIL + '@yandex.com'
        recipient_list = [author_email]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)

@receiver(post_save, sender=Reply)
def reply_accepted_notification(sender,instance, created, **kwargs):
    if not created:
        post_title = instance.post.title
        body = instance.body
        reply_author_email = instance.author
        print(f'reply_author_email = {reply_author_email}')
        author_name = instance.post.author.username

        # Оповещение о том, что отклик принят
        subject = 'Ура! Ваш отклик принят!'
        message = f'''
                Ваш отклик на пост "{post_title}" содержанием:
                {body} 
                был принят автором!
                Поздравляем!
                '''
        from_email = MY_EMAIL + '@yandex.com'
        recipient_list = [reply_author_email]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)