# -*- coding: utf-8 -*-
import datetime
import uuid
import os
import smtplib

from hashlib import md5

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email as valid_email
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from django.template import Context

from accounts.models import EmailVerification, PasswordResetCode
from accounts.models import ExtendedProfile

from social.pipeline.user import get_username as social_get_username
from social.pipeline.user import create_user as social_create_user


def generate_unique_username(email):
    """
    Genera un username unico
    params
      email string email del usuario a encodear
    return
      string encodeado de 24 chars
    """
    return md5(email).digest().encode('base64')[:-1]


def validate_email(email):
    try:
        valid_email(email)
        return True
    except ValidationError:
        return False


def valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def date_greater_than(datestring, years):
    if not valid_date(datestring):
        return False
    try:
        ds_years = int(datestring.split('/')[2])
    except:
        return False

    return (ds_years <= (datetime.datetime.now().year - years))


def activate_email(code):
    '''
    Verify an email with the code sent it.
    '''
    try:
        ev = EmailVerification.objects.get(code=code)
        ev.user.is_active = True
        ev.user.save()
        verified = True
        # TODO need to verify the account
    except EmailVerification.DoesNotExist:
        verified = False

    return verified


def create_email_verification_url(request, user):
    '''
    Generate a code for email verification.
    '''
    code = uuid.uuid4().hex
    try:
        ev = EmailVerification.objects.get(user=user)
        ev.code = code
        ev.save()
    except EmailVerification.DoesNotExist:
        EmailVerification(user=user, code=code,
                          date_sent=timezone.now()).save()

    # Generate the verification url.
    activate_url = '{}://{}{}?code={}'.format(
        'https' if request.is_secure() else 'http',
        request.get_host(),
        reverse('accounts:email-verification'),
        code)

    return activate_url


def send_email_verification(email, activate_url):

    email_subject = _(u'Open BA ID - Activar cuenta')
    context = {
        'activate_url': activate_url,
    }
    email_message = render_to_string('accounts/email_message.html', context)
    email_message = email_message.strip('/n')  # Remove '\n' characters.

    em = EmailMessage(email_subject, email_message,
                      settings.DEFAULT_FROM_EMAIL, [email])

    em.content_subtype = 'html'
    em.send()


def create_password_reset_url(request, user):
    '''
    Generate a code for passoword reset.
    '''
    code = uuid.uuid4().hex
    try:
        ev = PasswordResetCode.objects.get(user=user)
    except PasswordResetCode.DoesNotExist:
        ev = PasswordResetCode(user=user)
    ev.code = code
    ev.consumed = False
    ev.date_sent = timezone.now()
    ev.save()

    # Generate the verification url.
    reset_url = '{}://{}{}{}'.format(
        'https' if request.is_secure() else 'http',
        request.get_host(),
        reverse('accounts:password-reminder'),
        code)

    return reset_url


def send_password_reset_email(email, reset_url):

    email_subject = _(u'Open BA ID - Recuper Contraseña')
    context = {
        'reset_url': reset_url,
    }
    email_message = render_to_string('accounts/password_reset_email.html',
                                     context)
    email_message = email_message.strip('/n')  # Remove '\n' characters.

    em = EmailMessage(email_subject, email_message,
                      settings.DEFAULT_FROM_EMAIL, [email])

    em.content_subtype = 'html'
    em.send()


def user_has_profile(user):
    """ Will verify that the user has a completed valid profile
    params:
        user request
    return
        boolean
    """
    has_profile = True
    try:
        ep = ExtendedProfile.objects.get(user=user)
        if not ep.tipo_documento or not ep.numero_documento or not ep.nombre or \
           not ep.apellido or not ep.fecha_nacimiento or not ep.genero:
            has_profile = False
    except Exception:
        has_profile = False

    return has_profile


def get_username(strategy, details, user=None, *args, **kwargs):
    """
    Used in the pipeline of social auth.
    See: http://python-social-auth.readthedocs.org/en/latest/use_cases.html
    """
    result = social_get_username(strategy, details, user=user, *args, **kwargs)

    if details.get('email'):
        string = details.get('email')
    else:
        from random import random
        string = str(random())

    result['username'] = generate_unique_username(string)

    return result


def create_user(strategy, details, user=None, *args, **kwargs):
    """
    Used in the pipeline of social auth for creating user account.
    See: https://github.com/omab/python-social-auth/blob/master/social/pipeline/user.py#L58
    """
    result = social_create_user(strategy, details, user=user, *args, **kwargs)

    if result:
        if result.get('is_new'):
            if not result.get('user').email:
                return
    return result


def save_avatar(backend, user, response, *args, **kwargs):
    try:
        profile = ExtendedProfile.objects.get(user=user)
    except ExtendedProfile.DoesNotExist:
        profile = ExtendedProfile(user=user)

    if backend.name == 'facebook':
        try:
            profile.avatar = 'http://graph.facebook.com/{0}/picture?width=250&height=250'.format(
                response['id'])
            profile.save()
        except:
            pass
    elif backend.name == 'google-oauth2':
        try:
            profile.avatar = response['image']['url'].split('?sz=')[0] + '?sz=250'
            profile.save()
        except:
            pass
