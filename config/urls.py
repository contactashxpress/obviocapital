

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# URLs avec préfixe de langue (ex: /fr/, /en/, /ar/)
urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=False,  # / au lieu de /fr/ pour la langue par défaut
)