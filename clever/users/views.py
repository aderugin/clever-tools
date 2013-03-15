# -*- coding: utf-8 -*-
# Create your views here.
from django.views.generic import View
from django.views.generic import UpdateView
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.db.models import permalink
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from .models import RikitaviUser
from .models import UserChildren
from .forms import UserEditForm
from .forms import ChildrenForm
from .forms import RegistrationForm
from .forms import UserChangePasswordForm

import json
import urlparse


class FormMixinView(object):
    def get_ajax_kwargs(self, error=False):
        return {}

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            to_json_response = self.get_ajax_kwargs(error=False)
            to_json_response['status'] = 1
            return HttpResponse(json.dumps(to_json_response), mimetype='application/json')
        return super(FormMixinView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            to_json_response = self.get_ajax_kwargs(error=True)
            to_json_response['status'] = 0
            to_json_response['errors'] = form.errors
            to_json_response['otherErrors'] = form.non_field_errors()
            return HttpResponse(json.dumps(to_json_response), mimetype='application/json')
        return self.render_to_response(self.get_context_data(form=form))

    @permalink
    def get_success_url(self):
        return ("account_detail", (), {})


class UserMixin(object):
    def get_user(self):
        """
        Получаем пользователя Rikitavi для работы с профилем
        """
        if not getattr(self, 'user', None):
            try:
                user = self.request.user
                if not user:
                    raise Http404()
                self.user = RikitaviUser.objects.get(pk=user.pk)
            except Exception:
                raise Http404()
        return self.user


class UserMixinView(UserMixin, FormMixinView):
    model = RikitaviUser

    def get_object(self, query_set=None):
        if not getattr(self, 'object', None):
            self.object = self.get_user()
        return self.object


class ChildrenMixinView(FormMixinView, UserMixin):
    model = UserChildren
    form_class = ChildrenForm


class ProfileView(UserMixinView, UpdateView):
    """
    Контроллер обработки сохранения данных профиля пользователя
    """
    template_name = "accounts/index.html"
    form_class = UserEditForm

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        object = self.get_object()
        context['password_form'] = UserChangePasswordForm(object)
        context['child_add_form'] = ChildrenForm()

        forms = []
        for child in object.childrens.all():
            forms.append(ChildrenForm(instance=child))
        context['children_forms'] = forms

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm

    def form_valid(self, form):
        if not self.request.POST.get('remember_me', None):
            self.request.session.set_expiry(0)

        login(self.request, form.get_user())
        redirect_url = self.request.POST.get('next', None) or '/account/'

        if self.request.is_ajax():
            to_json_response = dict()
            to_json_response['status'] = 'OK'
            to_json_response['redirect_url'] = redirect_url
            return HttpResponse(json.dumps(to_json_response), mimetype='application/json')
        else:
            return HttpResponseRedirect(redirect_url)


class ModalLoginView(LoginView):
    template_name = "accounts/modal_login.html"


class AccountCheckExists(View):

    def get(self, request, *args, **kwargs):
        user_by_email = RikitaviUser.objects.filter(username=request.GET.get('email'))
        if (user_by_email.count() > 0):
            return HttpResponse('true')
        else:
            return HttpResponse('false')


class LogoutView(TemplateView):
    """
    Class based version of django.contrib.auth.views.logout
    """
    next_page = None
    template_name = 'account/logged_out.html'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        logout(self.request)
        redirect_to = request.REQUEST.get(self.redirect_field_name, '')
        if redirect_to:
            netloc = urlparse.urlparse(redirect_to)[1]
            # Security check -- don't allow redirection to a different host.
            if not (netloc and netloc != self.request.get_host()):
                return HttpResponseRedirect(redirect_to)
        if self.next_page:
            return HttpResponseRedirect(self.next_page)
        return HttpResponseRedirect("/")

    def get_context_data(self, **kwargs):
        #kwargs['redirect_field_name'] = self.get_success_url()
        kwargs['site'] = get_current_site(self.request)
        kwargs['site_name'] = kwargs['site'].name
        return super(LogoutView, self).get_context_data(**kwargs)


class RegisterView(FormView):
    """ RegisterView  /account/register/ """

    template_name = 'accounts/registration.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        cleaned_data = form.cleaned_data.copy()
        user = RikitaviUser()
        user.password = cleaned_data.get('password1')
        user.username, user.email = cleaned_data.get('email'), cleaned_data.get('email')
        user.first_name = cleaned_data.get('name')
        user.phone = cleaned_data.get('phone')
        user.save()
        return HttpResponseRedirect("/account/")


class PasswordChangeView(UserMixinView, UpdateView):
    """
    Контроллер обработки сохранения данных профиля пользователя
    """
    template_name = "accounts/index.html"
    form_class = UserChangePasswordForm

    @permalink
    def get_success_url(self):
        return ("account_detail", (), {})

    def form_valid(self, form):
        form.save()

        if self.request.is_ajax():
            to_json_response = dict()
            to_json_response['status'] = 1
            return HttpResponse(json.dumps(to_json_response), mimetype='application/json')
        return HttpResponseRedirect(self.request.path)

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.get_object()
        kwargs.pop('instance')
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(*args, **kwargs)


class ChildrenAddView(ChildrenMixinView, CreateView):
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.get_user()
        return super(ChildrenAddView, self).form_valid(form)

    def get_ajax_kwargs(self, error=False):
        if not error and getattr(self, 'object', None):
            object = self.object
            return {
                'form_action': reverse('account_child_edit', kwargs={'id': object.id})
            }
        return {}


class ChildrenEditView(ChildrenMixinView, UpdateView):
    pk_url_kwarg = 'id'
