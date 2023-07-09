import uuid
from urllib.parse import urlencode
from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation
from allauth.account.views import SignupView, LoginView, sensitive_post_parameters_m
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .forms import PostForm, CodeCheckForm
from .models import Post, VerificationCode, CustomUser
from Fans_Board import settings
from allauth.decorators import rate_limit
from django.views.decorators.debug import sensitive_post_parameters


class PostsList(ListView):
    model = Post
    ordering = '-post_created'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.email_verified:
    #         return self.handle_unverified_email()
    #     return super().dispatch(request, *args, **kwargs)


class PostUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


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

        # Send confirmation email
        # current_site = get_current_site(self.request)
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
        print('GET CODECHECK called')
        print(request)
        print(self.request)
        print(self.request.user)
        form = CodeCheckForm()
        user_id = request.GET.get('user_id')
        email_not_verified = request.GET.get('email_not_verified', '')
        print(f'CodeCheckView.email_not_verified = {email_not_verified}')
        return render(request, self.template_name,
                      {'form': form, 'user_id': user_id, 'email_not_verified': email_not_verified})

    def post(self, request):
        print('POST CODECHECK called')
        print(f'POINT 1: {self.request.user}')
        # Get the confirmation code entered by the user
        user_code = request.POST.get('verification_code')
        user_id = request.POST.get('user_id')

        # Query the VerificationCode model to check if the code matches for the given user
        try:
            verification = VerificationCode.objects.get(new_user_id=user_id, temp_code=user_code)
            user = CustomUser.objects.get(pk=user_id)
            user.email_verified = True
            user.save()
            print(f'POINT 2: {self.request.user}')


        except VerificationCode.DoesNotExist:
            form = CodeCheckForm()
            try_again = 'Verification code is incorrect. Please try again...'
            print(f'POINT 3: {self.request.user}')
            redirect_url = reverse('code_check') + f"?user_id={user_id}&try_again={try_again}"
            next_val = self.request.session.get('next')
            redirect_url += f"&next={next_val}"
            return redirect(redirect_url)

        # Redirect to the success URL
        print(f'POINT 4: {self.request.user}')
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
        print(f'EMAIL Verified? - {user.email_verified}')

        if user.email_verified:
            # If the user's email is confirmed, proceed with the default form_valid behavior
            return super().form_valid(form)
        else:
            print('REDIRECTING from CustomLoginView')
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


