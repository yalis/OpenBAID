# -*- coding: utf-8 -*-
import logging
import simplejson
import calendar
from datetime import *

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


NACIONALIDAD_POR_DEFECTO = 'AR'
PROVINCIA_POR_DEFECTO = 3
TD_DEFECTO = 1
GENERO_POR_DEFECTO = 1

logger = logging.getLogger(__name__)


class EmailVerification(models.Model):
    # TODO Queda pendiente verificacion de Juani. Si esto se hace complejo,
    # volverlo a poner como ForeignKey
    user = models.OneToOneField(User)
    code = models.CharField(max_length=60)
    date_sent = models.DateTimeField(auto_now_add=True)


class PasswordResetCode(models.Model):
    user = models.OneToOneField(User)
    code = models.CharField(max_length=60)
    consumed = models.BooleanField(default=False)
    date_sent = models.DateTimeField()


class TipoDocumento(models.Model):
    class Meta:
        ordering = ["tipo", ]

    tipo = models.CharField(null=False, max_length=30, blank=False, unique=True)

    def __repr__(self):
        return "<Tipo Documento:{tipo}>".format(tipo=self.tipo)


class Nacionalidad(models.Model):
    class Meta:
        ordering = ["nombre", ]
    nombre = models.CharField(null=False, blank=True, max_length=50,
                              unique=True)
    codigo = models.CharField(null=False, blank=True, max_length=3,
                              unique=True)


class Provincia(models.Model):
    nombre = models.CharField(null=False, blank=False, max_length=100,
                              unique=True)


class Localidad(models.Model):
    nombre = models.CharField(null=False, blank=False, max_length=100)
    provincia = models.ForeignKey(Provincia)


class Genero(models.Model):
    nombre = models.CharField(null=False, blank=False, max_length=20)


class ExtendedProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    tipo_documento = models.ForeignKey(TipoDocumento, null=True, blank=True)
    numero_documento = models.CharField(max_length=100, null=True, blank=True)
    nacionalidad = models.ForeignKey(Nacionalidad, null=True, blank=True)
    altura = models.IntegerField(null=True)
    piso = models.CharField(null=True, blank=True, max_length=50)
    departamento = models.CharField(null=True, blank=True, max_length=50)
    localidad = models.ForeignKey(Localidad, null=True)
    comuna = models.CharField(null=True, blank=True, max_length=100)
    email_alternativo = models.CharField(null=True, blank=True, max_length=100)
    cuit_cuil = models.CharField(null=True, blank=True, max_length=100)
    provincia = models.ForeignKey(Provincia, null=True, blank=True)

    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellido = models.CharField(max_length=255, blank=True, null=True)
    genero = models.CharField(max_length=100, choices=[('M', 'Male'), ('F', 'Female')], null=True)
    fecha_nacimiento = models.DateField(null=True)
    numero_telefono = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    codigo_postal = models.CharField(max_length=255, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def profile(cls, username):
        try:
            p = ExtendedProfile.objects.filter(user__username=username).first()
        except Exception as e:
            logger.error(e)
            p = None
        return p


class DeletedUser(models.Model):
    user_information = models.TextField()
    deleted_date = models.DateField(auto_now=True)
    identifier = models.TextField(null=False, blank=False, db_index=True)


class UserInfo(object):

    @classmethod
    def get_by_user(cls, user):
        """
        This classmethod belongs to `django-oidc-provider`.
        See: https://github.com/juanifioren/django-oidc-provider/blob/v0.2.x/DOC.md#standard-claims
        """
        ep = ExtendedProfile.objects.get(user=user)
        class bare(object): pass

        bare.given_name = ep.nombre
        bare.family_name = ep.apellido
        bare.picture = ep.avatar
        bare.gender = ep.genero
        bare.birthdate = ep.fecha_nacimiento.isoformat() if ep.fecha_nacimiento else ''
        bare.updated_at = ep.fecha_modificacion.isoformat() if ep.fecha_modificacion else ''
        bare.email = user.email
        bare.email_verified = user.is_active
        bare.address_street_address = ep.direccion
        bare.address_locality = ep.localidad.nombre if ep.localidad else ''
        bare.address_region = ep.provincia.nombre if ep.provincia else ''
        bare.address_country = ep.nacionalidad.nombre if ep.nacionalidad else ''
        bare.address_postal_code = ep.codigo_postal
        bare.phone_number = ep.numero_telefono

        return bare
