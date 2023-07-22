import django_filters
from .models import Reply, Post


class ReplyFilter(django_filters.FilterSet):
    post = django_filters.ModelChoiceFilter(queryset=Post.objects.all(), field_name='post', to_field_name='title')

    class Meta:
        model = Reply
        fields = ['post']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.filters['post'].queryset = Post.objects.filter(author=user)
