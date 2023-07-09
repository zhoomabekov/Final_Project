from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = [
            'categories',
            'title',
            'body'
        ]

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args,
                                       **kwargs)  # переопределяем init для того, чтобы использовать названия Категорий
        self.fields['categories'].label_from_instance = lambda obj: obj.name


class CodeCheckForm(forms.Form):
    verification_code = forms.CharField(label='Verification Code')
