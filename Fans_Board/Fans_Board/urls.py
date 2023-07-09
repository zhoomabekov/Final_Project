from django.contrib import admin
from django.urls import path, include
from allauth import account

# from ckeditor_uploader.urls import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('', include('fanpage.urls')),
    path('accounts/', include('allauth.urls')),
    path('ckeditor', include('ckeditor_uploader.urls')),

]
