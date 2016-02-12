# Open BA ID

**Open BA ID** es un sistema de autenticación basada en el protocolo OpenID Connect desarrollado por la Dirección General de Gobierno Electrónico.

# Tabla de contenidos
- [Sobre Open BA ID](#sobre-ba-id)
- [Requerimientos](#requerimientos)
- [Instalación](#instalacion)
- [Configuración](#configuracion)

## Sobre Open BA ID
Open BA ID es un sistema de autenticación único que permite conectar cualquier aplicación que requiera un sistema de registro y autenticación.

El sistema está basado en el protocolo de [OpenID Connect](https://openid.net/), dado que permite que Open BA ID sea proveedor del servicio para cualquier aplicación web o móvil de Gobierno que quiera incorporarse.

## Requerimientos
- Python 2.7

## Instalación

Recomendamos activar un `virtualenv`. Para luego:

```
# Clonar el proyecto.
$ git clone https://github.com/gcba/OpenBAID.git
$ cd OpenBAID

# Instalar dependencias y correr las migraciones.
$ pip install -r requirements.txt
$ python manage.py migrate

# Cargar paises, provincias y localidades.
$ python manage.py loadinitialdata

# Generar una RSA Key para el servidor OpenID.
$ python manage.py creatersakey
```

Luego para acceder creamos un usuario superuser.

```
$ python manage.py createsuperuser
```

Levantamos la aplicación

```
$ python manage.py runserver
```

[http://localhost:8000](http://localhost:8000)

## Configuración

El archivo se encuentra en `baid/settings.py`.

##### Settings de Django

- DEBUG. `bool`. Si es un ambiente de producción debería estar en `False`.
- SITE_URL. `str`. Url de la aplicación. Por ejemplo `http://localhost:8000`.
- SECRET_KEY. `str`. Clave única y secreta requerida por Django.

##### Redes Sociales

Permite a tus usuarios loguearse con su red social preferida.

- SOCIAL_AUTH_GOOGLE_OAUTH2_KEY y SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET. [Más info](https://console.developers.google.com).
- SOCIAL_AUTH_FACEBOOK_KEY y SOCIAL_AUTH_FACEBOOK_SECRET. [Más info](https://developers.facebook.com/).

##### Recaptcha para login y registro.

- RECAPTCHA_PUBLIC_KEY y RECAPTCHA_PRIVATE_KEY. [Más info](https://www.google.com/recaptcha/intro/index.html).
