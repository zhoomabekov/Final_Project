from django.urls import path
from .views import PostsList, PostDetail, PostCreate, PostUpdate, PostDelete, CodeCheckView, CustomSignupView, \
    CustomLoginView, PrivateReplyView, RepliesView, ReplyDelete, replyAccepted

urlpatterns = [
    path('', PostsList.as_view(), name='posts_list'),
    path('accounts/signup/', CustomSignupView.as_view(), name='custom_signup'),
    path('accounts/login/', CustomLoginView.as_view(), name='custom_login'),
    path('posts/', PostsList.as_view(), name='posts_list'),
    path('post/<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('post/create/', PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/update', PostUpdate.as_view(), name='post_update'),
    path('post/<int:pk>/delete', PostDelete.as_view(), name='post_delete'),
    path('codecheck/', CodeCheckView.as_view(), name='code_check'),
    path('post/<int:post_id>/reply/', PrivateReplyView.as_view(), name='private_reply'),
    path('replies/', RepliesView.as_view(), name='replies_list'),
    path('reply/<int:pk>/delete', ReplyDelete.as_view(), name='reply_delete'),
    path('reply/<int:pk>/accept', replyAccepted, name='reply_accept'),

]
