# -*- coding: utf-8 -*-
from urllib import quote

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from oidc_provider.lib.claims import AbstractScopeClaims


def after_userlogin_hook(request, user, client):
    # This must be lazily imported!.
    from accounts.models import ExtendedProfile

    try:
        ep = ExtendedProfile.objects.get(user=user)
        ep = ep.tipo_documento and ep.numero_documento and ep.nombre and ep.apellido and ep.fecha_nacimiento
    except ExtendedProfile.DoesNotExist:
        ep = False

    # Check if profile is complete.
    if not ep:
        url = reverse('accounts:profile-complete') + '?' + \
              REDIRECT_FIELD_NAME + '=' + quote(request.get_full_path())

        return HttpResponseRedirect(url)

    return None


def default_sub_generator(user):
    return "https://id.buenosaires.gob.ar/openid/{ue}/".format(ue=user.email)


class CustomScopeClaims(AbstractScopeClaims):

    def setup(self):
        from accounts.models import ExtendedProfile
        try:
            self.ep = ExtendedProfile.objects.get(user=self.user)
        except ExtendedProfile.DoesNotExist:
            # Create an empty model object.
            self.ep = None

    def scope_extra(self, user):

        dic = {
            'tipo_documento': getattr(self.ep.tipo_documento, 'tipo', None) if getattr(self.ep, 'tipo_documento', None) else None,
            'numero_documento': getattr(self.ep, 'numero_documento', None),
            'cuit_cuil': getattr(self.ep, 'cuit_cuil', None),
        }

        return dic
