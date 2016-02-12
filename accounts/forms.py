# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import PasswordChangeForm
from django.forms.widgets import EmailInput, PasswordInput, HiddenInput
from django.contrib.auth import get_user_model
from django import forms

from captcha.fields import ReCaptchaField

User = get_user_model()

class PasswordMixinFormValidation(forms.Form):
    """
    Validación básica, longitud de contraseña y que sean iguales
    """
    def clean_password(self):
        if self.data['password']:
            if self.data['password'] != self.data['password_repeat']:
                raise forms.ValidationError(_(u'Las contraseñas deben ser igual.'))
            if (len(self.data['password']) <= 4):
                raise forms.ValidationError(_(u'Contraseñas deben tener mas de 4 caracteres.'))

        return self.data['password']

    def clean(self, *args, **kwargs):
        self.clean_password()
        return super(PasswordMixinFormValidation, self).clean(*args, **kwargs)


class LoginUserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': _(u'Correo Electrónico')
            }
        )
        self.fields['password'].widget = PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _(u'Contraseña')
            }
        )

        self.fields['next'].widget = HiddenInput()

    def clean_email(self):   # todo DRY
        if self.data['email']:
            email = self.data['email'].lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    _(u'El usuario no existe')

                )
        return self.data['email']

    def clean(self, *args, **kwargs):  # todo DRY
        self.clean_email()
        return super(LoginUserForm, self).clean(*args, **kwargs)


class BaidPasswordChangeForm(PasswordChangeForm):
    """
    Password Chage Form
    """
    def __init__(self, *args, **kwargs):

        super(BaidPasswordChangeForm, self).__init__(*args, **kwargs)

        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs = \
                {'class': 'form-control input-lg'}

        self.fields['old_password'].widget.attrs['placeholder'] = \
            _(u'Contraseña actual')

        self.fields['new_password1'].widget.attrs['placeholder'] = \
            _(u'Ingresá tu nueva contraseña')

        self.fields['new_password2'].widget.attrs['placeholder'] = \
            _(u'Ingresá de nuevo tu nueva contraseña')


class RegisterUserForm(PasswordMixinFormValidation):
    email = forms.EmailField()
    password = forms.CharField()
    password_repeat = forms.CharField()
    if settings.RECAPTCHA:
        captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'es'})
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = EmailInput(
            attrs={
                'class': 'form-control input-lg',
                'placeholder': _(u'Correo Electrónico')
            }
        )
        self.fields['password'].widget = PasswordInput(
            attrs={
                'class': 'form-control input-lg',
                'placeholder': _(u'Contraseña')
            }
        )
        self.fields['password_repeat'].widget = PasswordInput(
            attrs={
                'class': 'form-control input-lg',
                'placeholder': _(u'Confirmar Contraseña')
            }
        )
        # self.fields['captcha'].widget.attrs = \
        #     {'class': 'form-control input-lg'}
        self.fields['next'].widget = HiddenInput()


class PasswordReminderForm(forms.Form):
    """
    Password Reminder Form
    Recibe email del usuario, valida exista y si existe envia un link
    para recuperar la contraseña
    """
    email = forms.EmailField()
    captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'es'})
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):

        super(PasswordReminderForm, self).__init__(*args, **kwargs)

        self.fields['next'].widget=HiddenInput()
        self.fields['email'].widget=EmailInput(
            attrs={
                'placeholder': _(u'Correo electrónico'),
                'class': 'form-control input-lg'
            })
        self.fields['captcha'].widget.attrs = \
            {'class': 'form-control input-lg'}

    def clean_email(self):
        if self.data['email']:
            email = self.data['email'].lower()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    _(u'El email no esta asociado a ninguna cuenta existente')

                )
        return self.data['email']

    def clean(self, *args, **kwargs):
        self.clean_email()
        return super(PasswordReminderForm, self).clean(*args, **kwargs)


class EmailSendForm(PasswordReminderForm):

    def clean_email(self):
        if self.data['email']:
            email = self.data['email'].lower()
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    raise forms.ValidationError(
                        _(u'Tu correo electrónico esta activado. Intenta ingresar.'))
            except User.DoesNotExist:
                raise forms.ValidationError(
                    _(u'El email no esta asociado a ninguna cuenta existente')

                )
        return self.data['email']

class PasswordResetForm(PasswordMixinFormValidation):
    """
    Password Reset Form
    """
    password = forms.CharField()
    password_repeat = forms.CharField()
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):

        super(PasswordResetForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget = PasswordInput(
            attrs={
                'placeholder': _(u'Ingresá tu nueva contraseña'),
                'class': 'form-control input-lg'
            }
        )

        self.fields['password_repeat'].widget = PasswordInput(
            attrs={
                'placeholder': _(u'Confirmar nueva contraseña'),
                'class': 'form-control input-lg'
            }
        )
        self.fields['next'].widget = HiddenInput()
