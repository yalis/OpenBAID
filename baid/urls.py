from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


handler404 = 'baid.views.handler404'
handler500 = 'baid.views.handler500'


urlpatterns = patterns(
    '',
    url(r'^$', 'baid.views.home', name='home'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    url('', include('social.apps.django_app.urls', namespace='social')),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
