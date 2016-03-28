# -*- coding: utf-8 -*-
import json
import logging

from datetime import date
from uuid import uuid4
from urllib import quote
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.template import RequestContext
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, resolve_url, render_to_response
from django.template.loader import render_to_string, select_template
from django.views.generic import FormView
from django.utils.http import is_safe_url
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.utils import ErrorList
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from accounts.decorators import *
from accounts.forms import *
from accounts.models import *
from accounts.utils import *

from social.backends.open_id import OpenIdConnectAuth
from social.exceptions import AuthMissingParameter

logger = logging.getLogger(__name__)


def login(request):
    """
    Displays the login form and handles the login action.
    It's a rewrite of django login view, this requires the end user to
    authenticate using email instead of username.
    """

    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))

    if redirect_to:
        redirect_path = '?{0}={1}'.format(REDIRECT_FIELD_NAME,
                                          quote(redirect_to))

    if request.user.is_authenticated():
        return redirect(redirect_to or reverse('accounts:profile'))

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            email = email.lower()
            try:
                # TODO Should use something different, we can't actually
                # insert the records, because in current baid we have
                # users with email greater than 30 chars
                user = User.objects.get(email=email)
                auth_user = authenticate(username=user.username,
                                         password=password)
                if auth_user:
                    if not user.is_active:
                        activate_url = create_email_verification_url(request, user)
                        if redirect_to:
                            activate_url += redirect_path
                        send_email_verification(email, activate_url)
                        return render(request, 'accounts/email_sent.html', {
                            'email': user.email,
                        })
                    # Log the user in.
                    auth_login(request, auth_user)
                    return redirect(redirect_to or reverse('accounts:profile'))
                else:
                    msg = _(u'El correo electrónico y contraseña son invalidos.')
                    messages.add_message(request, messages.ERROR, msg)
            except User.DoesNotExist:
                msg = _(u'El usuario no existe')
                messages.add_message(request, messages.ERROR, msg)
        else:
            msg = _(u'Falta correo electrónico o contraseña')
            messages.add_message(request, messages.ERROR, msg)

    # Create the url for registration and password recovery.
    register_url = reverse('accounts:register')
    reset_url = reverse('accounts:password-reminder')
    if redirect_to:
        redirect_path = '?{0}={1}'.format(REDIRECT_FIELD_NAME,
                                          quote(redirect_to))
        register_url += redirect_path
        reset_url += redirect_path

    context = {
        REDIRECT_FIELD_NAME: redirect_to,
        'register_url': register_url,
        'reset_url': reset_url,
    }

    return render(request, 'accounts/login.html', context)


def logout(request):
    auth_logout(request)

    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))

    return HttpResponseRedirect(redirect_to or reverse('accounts:login'))


class RedirectFormMixin(FormView):
    """
    Redirect to Form Mixin
    Mixin View agrega funcionalidad de redirect("next") a los Formviews que requieran.
    * Heredar primero
    """

    @property  # workaround
    def redirect_to(self):
        """
        Indica la URL a la que necesita redireccionarse en caso de venir desde un cliente o cualquier pagina
        :return:
        """
        # todo DRY, intecionalmente repetido para no quebrar, se armo un quilombete con un revert donde se quito codigo
        redirect_to = self.request.POST.get(REDIRECT_FIELD_NAME, self.request.GET.get(REDIRECT_FIELD_NAME, ''))

        return redirect_to

    @property
    def redirect_path(self):
        """
        Redirect path
        :return:
        """
        if self.redirect_to:
            return '?{0}={1}'.format(REDIRECT_FIELD_NAME, quote(self.redirect_to))
        return ''

    def get_redirect_to_value(self):
        """
        Obtiene/retorna valor de "Next" en caso de existir/recibirlo via GET o POST
        """
        return self.request.POST.get(
            REDIRECT_FIELD_NAME,
            self.request.GET.get(REDIRECT_FIELD_NAME, '')
        )

    def get_redirect_url(self, multiple_params=False):
        """
        Retorna URL lista para concatenar
        Ejemplo: &next=REDIRECT_VALUE
        """
        if self.get_redirect_to_value():
            url = '{0}next={1}'.format(
                '&' if multiple_params else '?',
                quote(self.get_redirect_to_value()))
        else:
            url = ''

        return url

    def get_initial(self):
        """
        Valor Inicial para todos los Formview Childs interesados.
        """
        redirect_to = self.get_redirect_to_value()
        return {'next': redirect_to}


class LoginUserView(RedirectFormMixin):
    """
    Login User View
    @watch_logins
    """
    form_class = LoginUserForm
    template_name = 'accounts/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():  # workaround se fue todo a la nada con un revert..
            return redirect(self.redirect_to or reverse('accounts:profile'))

        return super(LoginUserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginUserView, self).get_context_data(**kwargs)

        redirect_url = self.get_redirect_url()

        context['next'] = self.get_redirect_to_value()

        context['register_url'] = reverse('accounts:register')
        context['register_url'] += redirect_url

        context['reset_url'] = reverse('accounts:password-reminder')
        context['reset_url'] += redirect_url

        return context

    def form_valid(self, form):
        email = form.cleaned_data['email'].lower()
        password = form.cleaned_data['password']

        user = User.objects.get(email=email)
        auth_user = authenticate(username=user.username, password=password)

        if auth_user:
            if not user.is_active:
                activate_url = create_email_verification_url(self.request, user)
                if self.redirect_to:
                    activate_url += self.redirect_path
                    send_email_verification(email, activate_url)
                    return render(self.request, 'accounts/email_sent.html', {'email': user.email})

            auth_login(self.request, auth_user)
            return redirect(self.redirect_to or reverse('accounts:profile'))

        else:
            form._errors['email'] = ErrorList([_(u'El correo electrónico y contraseña son invalidos.')])
            return self.form_invalid(form)

        return redirect(reverse('accounts:profile'))


class RegisterUserView(RedirectFormMixin):
    """
    Register user view
    """
    form_class = RegisterUserForm
    template_name = 'accounts/register.html'
    template_success_name = 'accounts/email_sent.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.get_redirect_to_value() or 'accounts:profile')

        return super(RegisterUserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RegisterUserView, self).get_context_data(**kwargs)

        context['next'] = self.get_redirect_to_value()

        return context

    def form_valid(self, form):
        email = form.cleaned_data['email'].lower()
        password = form.cleaned_data['password']

        if User.objects.filter(email=email).count():
            form._errors['email'] = ErrorList([_(u'El correo electrónico ya ha sido registrado. Intenta ingresar.')])
            return self.form_invalid(form)

        username = generate_unique_username(email)
        user = User.objects.create_user(username, email, password)
        user.is_active = False
        user.save()

        activate_url = create_email_verification_url(self.request, user)
        activate_url += self.get_redirect_url(multiple_params=True)

        send_email_verification(email, activate_url)

        return render_to_response(
            self.template_success_name, {'email': email},
            context_instance=RequestContext(self.request)
        )


def email_verification(request):
    code = request.GET.get('code', '')
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')

    error = not activate_email(code)

    login_url = reverse('accounts:login')
    if redirect_to:
        login_url += '?{}={}'.format(REDIRECT_FIELD_NAME, quote(redirect_to))

    context = {
        'error': error,
        'login_url': login_url,
    }

    return render(request, 'accounts/email_verification.html', context)


class EmailSendFormView(RedirectFormMixin):
    """
    Enviar un email para activar la cuenta del usuario.
    """
    form_class = EmailSendForm
    template_name = 'accounts/email_send.html'
    success_template_name = 'accounts/email_sent.html'

    def dispatch(self, request, *args, **kwargs):
        # Fill the email into the form if the user is logged.
        if request.user.is_authenticated():
            # If user is logged and active should not be here.
            if request.user.is_active:
                return redirect(self.get_redirect_url() or 'accounts:profile')
        return super(EmailSendFormView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email'].lower()
        user = User.objects.get(email=email)

        activate_url = create_email_verification_url(self.request, user)
        activate_url += self.get_redirect_url()

        send_email_verification(user.email, activate_url)

        return render_to_response(
            self.success_template_name,
            {'email': email},
        )


class PasswordReminderFormView(RedirectFormMixin):
    """
    Password Reset Form
    formulario para recordar passsword al usuario via email.
    """
    form_class = PasswordReminderForm
    template_name = 'accounts/password_reset_send.html'
    success_template_name = 'accounts/password_reset_sent.html'

    def form_valid(self, form):
        email = form.cleaned_data['email'].lower()
        user = User.objects.get(email=email)

        # Generar link (Reset URL)
        reset_url = create_password_reset_url(self.request, user)
        reset_url += self.get_redirect_url()

        # si esta Ok, enviar email
        send_password_reset_email(user.email, reset_url)

        # mostrar mensaje de enviado
        return render_to_response(
            self.success_template_name,
            {'email': email},
        )


class PasswordResetFormView(RedirectFormMixin):
    """
    Password change Form
    formulario
    """
    form_class = PasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    template_name_invalid_code = 'accounts/password_reset_invalid_code.html'

    def render_invalid_request(self):
        """
        Shortcut, DRY, used for multiples cases,
        for example when the reset code is invalid or was consumed...
        :return:
        """

        return render_to_response(
            self.template_name_invalid_code, {},
            context_instance=RequestContext(self.request)
        )

    def dispatch(self, *args, **kwargs):
        reset_code = self.kwargs['reset_code']

        try:
            prc = PasswordResetCode.objects.get(code=reset_code)

            if prc.consumed:
                messages.error(self.request, _(u'EL link de recuperar contraseña ya fue usado. Intentalo nuevamente.'))

                return self.render_invalid_request()

        except PasswordResetCode.DoesNotExist:
            messages.error(self.request, _(u'Ocurrio un error, el link de recuperar contraseña es inválido.'))

            return self.render_invalid_request()

        return super(PasswordResetFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PasswordResetFormView, self).get_context_data(*args, **kwargs)
        context['code'] = self.kwargs['reset_code']
        return context

    def form_valid(self, form):

        password = form.cleaned_data['password']

        # seteamos nuevo password.
        prc = PasswordResetCode.objects.get(code=self.kwargs['reset_code'])

        prc.user.set_password(password)
        prc.user.save()

        login_url = reverse('accounts:login')
        login_url += self.get_redirect_url()

        return HttpResponseRedirect(login_url)


# yalis OpenID Connect integration.
class PocOpenId(OpenIdConnectAuth):
    name = 'poc'

    expire = 6000
    #redirect_uri = 'http://192.168.33.10:9000/complete/rerepoc'
    REDIRECT_STATE = False
    STATE_PARAMETER = True

    URL_ROOT = 'http://django-oidc-provider.dev:8000/openid'
    AUTHORIZATION_URL = '{0}/authorize/'.format(URL_ROOT)
    ACCESS_TOKEN_URL = '{0}/token/'.format(URL_ROOT)
    ACCESS_TOKEN_METHOD = 'POST'
    ID_TOKEN_ISSUER = 'http://localhost:8000/openid'

    def get_user_details(self, response):
        logger.debug(' ####### response in get_user_details : ' + str(response))

        # TODO: implementar user_data() para traer la info del usuario desde /openid/userinfo
        values = {'username': 'tester', 'email': 'tester@testing.com', 'fullname': 'Tester Loco', 'first_name': 'Tester', 'last_name': 'Loco'}

        #"""Generate username from identity url"""
        #values = super(PocOpenId, self).get_user_details(response)
        # values['username'] = 'tester' # values.get('username') or urlparse.urlsplit(response.identity_url).netloc.split('.', 1)[0]
        return values

    def get_user_id(self, details, response):
        return self.id_token['sub']

#    def openid_url(self):
#        """Returns Poc authentication URL"""
# if not self.data.get('openid_poc_user'):
#    raise AuthMissingParameter(self, 'openid_poc_user')


#        return 'http://192.168.33.10:8000/openid'  # % self.data['openid_poc_user']


@login_required
@profile_required
def profile(request):
    ep = ExtendedProfile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'name': ep.nombre,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_complete(request):
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))

    tipos_documentos = [td.tipo for td in TipoDocumento.objects.all()]

    # Load objects or create them.
    try:
        ep = ExtendedProfile.objects.get(user=request.user)
    except ExtendedProfile.DoesNotExist:
        ep = ExtendedProfile(user=request.user)

    if ep.fecha_nacimiento:
        birthdate = '{}/{}/{}'.format(
            ep.fecha_nacimiento.day, ep.fecha_nacimiento.month, ep.fecha_nacimiento.year)
    else:
        birthdate = ''

    data = {
        'first_name': request.POST.get('first_name', ep.nombre or request.user.first_name or ''),
        'last_name': request.POST.get('last_name', ep.apellido or request.user.last_name or ''),
        'birthdate': request.POST.get('birthdate', birthdate or ''),
        'gender': request.POST.get('gender', ep.genero),
        'tipo_documento': request.POST.get(
            'tipo_documento',
            ep.tipo_documento.tipo if ep.tipo_documento else ''),
        'numero_documento': request.POST.get(
            'numero_documento',
            ep.numero_documento or ''),
    }

    error = {k: False for k in data.iterkeys()}

    if request.method == 'POST':

        # Data validation.
        error['first_name'] = not data['first_name']
        error['last_name'] = not data['last_name']
        error['tipo_documento'] = not (data['tipo_documento'] in tipos_documentos)
        error['numero_documento'] = not data['numero_documento']
        error['gender'] = not (data['gender'] in ['F', 'M'])
        error['birthdate'] = not valid_date(data['birthdate']) or \
                             not date_greater_than(data['birthdate'], years=13)

        # Check if there's no error.
        if all([not e for e in error.itervalues()]):
            ep.nombre = data['first_name']
            ep.apellido = data['last_name']
            birthdate = tuple([int(n) for n in data['birthdate'].split('/')])
            ep.fecha_nacimiento = date(*(tuple(reversed(birthdate))))
            ep.genero = data['gender']
            ep.tipo_documento = TipoDocumento.objects.get(tipo=data['tipo_documento'])
            ep.numero_documento = data['numero_documento']

            ep.save()

            return redirect(redirect_to or reverse('accounts:profile'))

    # Hide the navigation when we have an OpenID request.
    hide_nav = 'client_id' in redirect_to

    context = {
        'user': request.user,
        'hide_nav': hide_nav,
        'error': error,
        'data': data,
        'tipos_documentos': tipos_documentos,
        REDIRECT_FIELD_NAME: redirect_to,
    }
    return render(request, 'accounts/profile_complete.html', context)


@login_required
@profile_required
def profile_extra(request):
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))

    nacionalidades = Nacionalidad.objects.all()
    provincias = Provincia.objects.all()

    # Load objects or create them.
    try:
        ep = ExtendedProfile.objects.get(user=request.user)
    except ExtendedProfile.DoesNotExist:
        ep = ExtendedProfile(user=request.user)

    data = {
        'nacionalidad': request.POST.get('nacionalidad',
                                         ep.nacionalidad.codigo if ep.nacionalidad else ''),
        'provincia': request.POST.get('provincia',
                                      ep.provincia.id if ep.provincia else ''),
        'localidad': request.POST.get('localidad',
                                      ep.localidad.id if ep.localidad else ''),
        'departamento': request.POST.get('departamento', ep.departamento or ''),
        'domicilio': request.POST.get('domicilio',
                                      ep.direccion or ''),
        'postal_code': request.POST.get('postal_code',
                                        ep.codigo_postal or ''),
        'comuna': request.POST.get('comuna', ep.comuna or ''),
        'phone_number': request.POST.get('phone_number', ep.numero_telefono or ''),
        'cuil': request.POST.get('cuil', ep.cuit_cuil or ''),
        'email_alternativo': request.POST.get('email_alternativo', ep.email_alternativo or ''),
    }

    error = {k: False for k in data.iterkeys()}
    not_error = True

    if request.method == 'POST':

        required = request.GET.get('required', '').split(',')

        if data['nacionalidad'] or ('nacionalidad' in required):
            error['nacionalidad'] = not (data['nacionalidad'] in [n.codigo for n in nacionalidades])
            if not error['nacionalidad']:
                ep.nacionalidad = [n for n in nacionalidades \
                                   if (n.codigo == data['nacionalidad'])][0]
        else:
            ep.nacionalidad = None

        if data['provincia'] or ('provincia' in required):
            error['provincia'] = not (data['provincia'] in [str(n.id) for n in provincias])
            if not error['provincia']:
                ep.provincia = [p for p in provincias \
                                if (str(p.id) == data['provincia'])][0]
        else:
            ep.provincia = None

        if data['localidad'] or ('localidad' in required):
            if data['provincia']:
                localidades = Localidad.objects.filter(provincia=data['provincia'])
            else:
                localidades = []
            error['localidad'] = not (data['localidad'] in [str(l.id) for l in localidades])
            if not error['localidad']:
                ep.localidad = [l for l in localidades \
                                if (str(l.id) == data['localidad'])][0]
        else:
            ep.localidad = None

        if data['departamento'] or ('departamento' in required):
            # TODO: Need a better validation.
            error['departamento'] = not (data['departamento'])
            if not error['departamento']:
                ep.departamento = data['departamento']
        else:
            ep.departamento = ''

        if data['domicilio'] or ('domicilio' in required):
            # TODO: Need a better validation.
            error['domicilio'] = not (data['domicilio'])
            if not error['domicilio']:
                ep.direccion = data['domicilio']
        else:
            ep.direccion = ''

        if data['postal_code'] or ('postal_code' in required):
            # TODO: Need a better validation.
            error['postal_code'] = not (data['postal_code'])
            if not error['postal_code']:
                ep.codigo_postal = data['postal_code']
        else:
            ep.codigo_postal = ''

        if data['comuna'] or ('comuna' in required):
            # TODO: Need a better validation.
            error['comuna'] = not (data['comuna'])
            if not error['comuna']:
                ep.comuna = data['comuna']
        else:
            ep.comuna = ''

        if data['phone_number'] or ('phone_number' in required):
            # TODO: Need a better validation.
            error['phone_number'] = not (data['phone_number'])
            if not error['phone_number']:
                ep.numero_telefono = data['phone_number']
        else:
            ep.numero_telefono = ''

        if data['cuil'] or ('cuil' in required):
            # TODO: Need a better validation.
            error['cuil'] = not (data['cuil'])
            if not error['cuil']:
                ep.cuit_cuil = data['cuil']
        else:
            ep.cuit_cuil = ''

        if data['email_alternativo'] or ('email_alternativo' in required):
            # TODO: Need a better validation.
            error['email_alternativo'] = not (data['email_alternativo'])
            if not error['email_alternativo']:
                ep.email_alternativo = data['email_alternativo']
        else:
            ep.email_alternativo = ''

        not_error = all([not e for e in error.itervalues()])
        if not_error:
            ep.save()
            return HttpResponseRedirect(redirect_to or reverse('accounts:profile'))

    context = {
        'user': request.user,
        'error': error,
        'error_exist': not not_error,
        'data': data,
        'nacionalidades': nacionalidades,
        'provincias': provincias,
        'next': redirect_to,
    }
    return render(request, 'accounts/profile_extra.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def get_localidades(request):
    provincia_id = request.POST.get('provincia_id', '')

    try:
        result = Localidad.objects.filter(provincia=provincia_id)
        result = [[e.id, e.nombre] for e in result]
    except:
        result = None

    result = result if result else []

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
@profile_required
def data(request):
    context = {
        'email': request.user.email,
    }
    return render(request, 'accounts/data.html', context)


@login_required
def change_password(request):
    context = {}

    if request.method == 'POST':
        form = BaidPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        form = BaidPasswordChangeForm(user=request.user)
    context['form'] = form
    return render(request, 'accounts/change_password.html', context)


@login_required
def delete_account(request):
    context = {}
    if request.method == 'POST':
        confirma = request.POST.get('borrar', False)
        if confirma:
            try:
                token = str(uuid4())
                user = request.user
                cache.set(token, user.username,
                          timeout=settings.USER_DELETION_TTL)
                emails = ['registration/default/delete_email_subject.txt',
                          'registration/default/delete_email_subject.txt']
                subject = render_to_string(select_template(emails).name,
                                           {'site': settings.SITE_URL})
                delete_url = 'accounts:registration-confirm-deletion'
                mail_vars = {'site': settings.SITE_URL,
                             'path': reverse(delete_url, args=[token])}
                emails = ['registration/default/delete_email.html',
                          'registration/default/delete_email.html']
                html_content = render_to_string(select_template(emails).name,
                                                mail_vars)
                msg = EmailMessage(subject.strip("\n"), html_content,
                                   settings.DEFAULT_FROM_EMAIL, [user.email])
                # Main content is now text/html
                msg.content_subtype = "html"
                msg.send()
                mensaje = _(u'Te enviamos instrucciones para completar el cierre de tu cuenta.')
                messages.success(request, mensaje)
                auth_logout(request)
            except Exception as e:
                logger.error("Obtained error {e}".format(e=e.message))
            return render(request, 'accounts/delete_account_success.html',
                          context)
    return render(request, 'accounts/delete_account.html', context)


def confirm_deletion(request, token):
    key = cache.get(token, None)
    if key:
        cache.delete(token)
        try:
            user = User.objects.get(username=key)
            back_user = serializers.serialize('json', [user])
            ex_profile = ExtendedProfile.objects.filter(user=user)
            back_profile = serializers.serialize('json', ex_profile)
            backup_info = {'user': back_user, 'extended_profile': back_profile}
            deleted_user = DeletedUser()
            deleted_user.identifier = user.email
            deleted_user.user_information = backup_info
            deleted_user.save()
            user.delete()
            messages.success(request, _(u'Tu cuenta ha sido borrada.'))
            auth_logout(request)
        except Exception as e:
            logger.error("Error {e} en borrado de usuario".format(e=e))
            msg = _(u'Tu cuenta no ha sido borrada. Por favor intentar nuevamente')
            messages.error(request, msg)
        return redirect('accounts:profile')
    else:
        msg = _(u'Tu cuenta no ha sido borrada. Por favor intentar nuevamente')
        messages.error(request, msg)
        return redirect('accounts:profile')
