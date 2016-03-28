# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import *


urlpatterns = [
    # User authentication
    url(r'^login/$', LoginUserView.as_view(), name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^register/$', RegisterUserView.as_view(), name='register'),

    # User email Verifications
    url(r'^email/verify/$', email_verification, name='email-verification'),
    url(r'^email/send/$', EmailSendFormView.as_view(), name='email_send'),

    # User change password options
    url(
        r'^password/reset/$', PasswordReminderFormView.as_view(),
        name='password-reminder'
    ),
    url(
        r'^password/reset/(?P<reset_code>[a-z0-9\-]+)/$',
        PasswordResetFormView.as_view(), name='password-reset'
    ),

    url(r'^change-password/$', change_password, name='change-password'),

    # User profile options
    url(r'^profile/$', profile, name='profile'),
    url(r'^profile/complete/$', profile_complete, name='profile-complete'),
    url(r'^profile/extra/$', profile_extra, name='profile-extra'),

    url(r'^get-localidades/$', get_localidades, name='get-localidades'),
    url(r'^data/$', data, name='data'),

    # User delete options
    url(r'^delete/$', delete_account, name='delete-account'),
    url(r'^confirm/(?P<token>[a-z0-9\-]+)/$', confirm_deletion, name='registration-confirm-deletion')
]
