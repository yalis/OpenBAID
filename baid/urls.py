from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from baid import views

handler404 = 'baid.views.handler404'
handler500 = 'baid.views.handler500'


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    url('', include('social.apps.django_app.urls', namespace='social')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
