import uuid
from urllib.parse import urlencode
from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation
from allauth.account.views import SignupView, LoginView, sensitive_post_parameters_m
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .tasks import hello

from .filters import ReplyFilter
from .forms import PostForm, CodeCheckForm, PrivateReplyForm
from .models import Post, VerificationCode, CustomUser, Reply
from Fans_Board import settings
from allauth.decorators import rate_limit
from django.views.decorators.debug import sensitive_post_parameters


class PostsList(ListView):
    model = Post
    ordering = '-post_created'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get(self, request):
        hello.delay()
        response = super().get(request)
        return response


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PrivateReplyForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PrivateReplyForm(request.POST)
        if form.is_valid():
            post = self.get_object()  # Get the current Post object
            user_reply = Reply.objects.create(
                post=post,
                author=self.request.user,
                body=form.cleaned_data.get('reply')
            )
            return redirect('post_detail', pk=post.pk)
        else:
            return self.get(request, *args, **kwargs)


class PostCreate(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user  # Pass the author to the form
        return kwargs


class PostUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_object(self, queryset=None):
        # Get the object based on the provided query and check if the current user has permission
        obj = super().get_object(queryset=queryset)

        if not obj.author == self.request.user:
            raise Http404("You do not have permission to edit this post.")

        return obj


class PostDelete(LoginRequiredMixin, DeleteView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')


@method_decorator(rate_limit(action="signup"), name="dispatch")
class CustomSignupView(SignupView):
    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        confirmation_code = str(uuid.uuid4().hex)[:10]

        # Save confirmation code and user id
        verification_code = VerificationCode.objects.create(
            new_user_id=form.save(request=self.request).id,
            temp_code=confirmation_code,
        )

        mail_subject = "Please Confirm Your E-mail Address"

        message = f"""
        Dear {form.cleaned_data['username']},

        Thank you for signing up to our website. Please confirm your e-mail address by putting the below code
        to the "Verification Code" box on the website:

        {confirmation_code}

        If you didn't sign up for an account, please ignore this message.

        Best regards,
        Your Website Team
        """

        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [form.cleaned_data['email']])
        print('FORM_VALID is called BEFORE REDIRECT')
        redirect_url = reverse("code_check") + f"?user_id={verification_code.new_user_id}"
        return redirect(redirect_url)


class CodeCheckView(View):
    template_name = 'code_check.html'
    success_url = '/posts/'  # URL to redirect after successful verification

    def get(self, request):
        form = CodeCheckForm()
        user_id = request.GET.get('user_id')
        email_not_verified = request.GET.get('email_not_verified', '')
        return render(request, self.template_name,
                      {'form': form, 'user_id': user_id, 'email_not_verified': email_not_verified})

    def post(self, request):
        # Get the confirmation code entered by the user
        user_code = request.POST.get('verification_code')
        user_id = request.POST.get('user_id')

        # Query the VerificationCode model to check if the code matches for the given user
        try:
            verification = VerificationCode.objects.get(new_user_id=user_id, temp_code=user_code)
            user = CustomUser.objects.get(pk=user_id)
            user.email_verified = True
            user.save()

        except VerificationCode.DoesNotExist:
            form = CodeCheckForm()
            try_again = 'Verification code is incorrect. Please try again...'
            redirect_url = reverse('code_check') + f"?user_id={user_id}&try_again={try_again}"
            next_val = self.request.session.get('next')
            redirect_url += f"&next={next_val}"
            return redirect(redirect_url)

        # Redirect to the success URL
        if self.request.session.get('next'):
            next_url = self.request.session.pop('next')
            return redirect(next_url)
        return redirect(self.success_url)


# class PostsSearch(ListView):
#     permission_required = ('portal_app.view_post')
#     model = Post
#     ordering = '-post_created'
#     template_name = 'posts_search.html'
#     context_object_name = 'posts'
#     paginate_by = 10


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        next_val = request.POST.get('next')  # Retrieve the value of the 'next' parameter
        request.session['next'] = next_val  # Store the value in the session for later use
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Perform your additional email confirmation check here
        email = form.cleaned_data.get('login')
        user = CustomUser.objects.get(email=email)

        if user.email_verified:
            # If the user's email is confirmed, proceed with the default form_valid behavior
            return super().form_valid(form)
        else:
            # If the user's email is not confirmed, redirect to the code_check page
            email_not_verified = '''
                        Your email was not verified. Please check your email inbox (or spam folder) 
                        copy the verification code and paste it below:
                        '''
            # Redirect the user to the CodeCheckView
            redirect_url = reverse(
                "code_check") + f"?user_id={user.id}&email_not_verified={email_not_verified}"
            next_val = self.request.session.get('next')
            redirect_url += f"&next={next_val}"
            return redirect(redirect_url)


class PrivateReplyView(LoginRequiredMixin, View):

    def get(self, request, post_id):
        form = PrivateReplyForm()
        context = {'form': form}
        return render(request, 'post.html', context)

    def post(self, request, post_id):
        form = PrivateReplyForm(request.POST)
        if form.is_valid():
            user_reply = Reply.objects.create(post=Post.objects.get(id=post_id), author=self.request.user,
                                              body=form.cleaned_data.get('reply'))
            # print('redirectiiiiiiiiiiing')
            # return redirect('posts_list')
        else:
            # Handle form validation errors here, if any
            pass


class RepliesView(LoginRequiredMixin, ListView):
    model = Reply
    ordering = '-reply_created'
    template_name = 'replies.html'
    context_object_name = 'replies'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        user_posts = Post.objects.filter(author=user)

        # Apply filter if the post is selected in the form
        reply_filter = ReplyFilter(self.request.GET, queryset=Reply.objects.filter(post__in=user_posts))
        return reply_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ReplyFilter(self.request.GET, queryset=self.get_queryset(), user=self.request.user)
        return context


class ReplyDelete(LoginRequiredMixin, DeleteView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    model = Reply
    template_name = 'reply_delete.html'
    success_url = reverse_lazy('replies_list')


@login_required
def replyAccepted(request, pk):
    reply = get_object_or_404(Reply, id=pk)
    post = reply.post
    if request.user == post.author:
        reply.accepted = True
        reply.save()
        messages.success(request, 'Reply Accepted!')
        return render(request, 'reply_accept.html')
    else:
        return render(request, 'reply_accept_authority.html')
