from django.urls import path
from .views import PostsList, PostDetail, PostCreate, PostUpdate, PostDelete, CodeCheckView, CustomSignupView, \
    CustomLoginView

urlpatterns = [
    path('', PostsList.as_view(), name='posts_list'),
    path('accounts/signup/', CustomSignupView.as_view(), name='custom_signup'),
    path('accounts/login/', CustomLoginView.as_view(), name='custom_login'),
    path('posts/', PostsList.as_view(), name='posts_list'),
    path('posts/<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('posts/create/', PostCreate.as_view(), name='post_create'),
    path('posts/<int:pk>/update', PostUpdate.as_view(), name='post_update'),
    path('posts/<int:pk>/delete', PostDelete.as_view(), name='post_delete'),
    path('codecheck/', CodeCheckView.as_view(), name='code_check'),

]
