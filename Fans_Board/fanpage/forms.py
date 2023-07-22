from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from .models import Post, CustomUser, Category


class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    body = forms.CharField(widget=CKEditorUploadingWidget())
    author = forms.ModelChoiceField(queryset=CustomUser.objects.none(), widget=forms.HiddenInput())
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = [
            'category',
            'title',
            'body',
            'author'
        ]

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label_from_instance = lambda obj: obj.name
        self.fields['author'].initial = author

        if author:
            self.fields['author'].initial = author
            self.fields['author'].queryset = CustomUser.objects.filter(id=author.id)

class CodeCheckForm(forms.Form):
    verification_code = forms.CharField(label='Verification Code')

class PrivateReplyForm(forms.Form):
    reply = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))