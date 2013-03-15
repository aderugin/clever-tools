from django.conf.urls import patterns, url
from .views import ProfileView
from .views import ModalLoginView
from .views import LoginView
from .views import LogoutView
from .views import RegisterView
from .views import PasswordChangeView
from .views import ChildrenAddView
from .views import ChildrenEditView
from .views import AccountCheckExists

urlpatterns = patterns('',
    url(r'^$', ProfileView.as_view(), name='account_detail'),
    url(r'^modal/login/$', ModalLoginView.as_view(), name='account_modal_login'),
    url(r'^check_exists/$', AccountCheckExists.as_view(), name='account_check_exists'),
    url(r'^login/$', LoginView.as_view(), name='account_login'),
    url(r'^logout/$', LogoutView.as_view(), name='account_logout'),
    url(r'^register/$', RegisterView.as_view(), name='account_registration'),
    url(r'^change_password/$', PasswordChangeView.as_view(), name='account_change_password'),
    url(r'^children/add$', ChildrenAddView.as_view(), name='account_child_add'),
    url(r'^children/(?P<id>\d+)/edit$', ChildrenEditView.as_view(), name='account_child_edit'),
)
