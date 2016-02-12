# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_information', models.TextField()),
                ('deleted_date', models.DateField(auto_now=True)),
                ('identifier', models.TextField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=60)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero_documento', models.CharField(max_length=100, null=True, blank=True)),
                ('altura', models.IntegerField(null=True)),
                ('piso', models.CharField(max_length=50, null=True, blank=True)),
                ('departamento', models.CharField(max_length=50, null=True, blank=True)),
                ('comuna', models.CharField(max_length=100, null=True, blank=True)),
                ('email_alternativo', models.CharField(max_length=100, null=True, blank=True)),
                ('cuit_cuil', models.CharField(max_length=100, null=True, blank=True)),
                ('nombre', models.CharField(max_length=255, null=True, blank=True)),
                ('apellido', models.CharField(max_length=255, null=True, blank=True)),
                ('genero', models.CharField(max_length=100, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('fecha_nacimiento', models.DateField(null=True)),
                ('numero_telefono', models.CharField(max_length=255, null=True, blank=True)),
                ('direccion', models.CharField(max_length=255, null=True, blank=True)),
                ('codigo_postal', models.CharField(max_length=255, null=True, blank=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now_add=True)),
                ('avatar', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Localidad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nacionalidad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(unique=True, max_length=50, blank=True)),
                ('codigo', models.CharField(unique=True, max_length=3, blank=True)),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PasswordResetCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=60)),
                ('consumed', models.BooleanField(default=False)),
                ('date_sent', models.DateTimeField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(unique=True, max_length=30)),
            ],
            options={
                'ordering': ['tipo'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='localidad',
            name='provincia',
            field=models.ForeignKey(to='accounts.Provincia'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendedprofile',
            name='localidad',
            field=models.ForeignKey(to='accounts.Localidad', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendedprofile',
            name='nacionalidad',
            field=models.ForeignKey(blank=True, to='accounts.Nacionalidad', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendedprofile',
            name='provincia',
            field=models.ForeignKey(blank=True, to='accounts.Provincia', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendedprofile',
            name='tipo_documento',
            field=models.ForeignKey(blank=True, to='accounts.TipoDocumento', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extendedprofile',
            name='user',
            field=models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
