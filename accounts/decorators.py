# -*- coding: utf-8 -*-
from urllib import quote

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from accounts.models import ExtendedProfile


def profile_required(func):
    """
    Check if the user have the BAID profile completed (info that
    MUST be completed). This decorator assumes that the user is logged.
    """
    def inner(request, *args, **kwargs):
        completed = True
        try:
            ep = ExtendedProfile.objects.get(user=request.user)
            if not ep.tipo_documento or not ep.numero_documento or \
               not ep.nombre or not ep.apellido or not ep.genero or \
               not ep.fecha_nacimiento:
                completed = False
        except ExtendedProfile.DoesNotExist:
            completed = False

        if completed:
            return func(request, *args, **kwargs)
        else:
            redirect_path = '?{0}={1}'.format(REDIRECT_FIELD_NAME,
                quote(request.path))
            url = reverse('accounts:profile-complete') + redirect_path
            return redirect(url)
    return inner