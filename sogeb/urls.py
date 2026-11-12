from django.conf import settings
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import robots_txt

urlpatterns = [
    # Administration à une adresse non standard (cahier des charges, 6.3)
    path("gestion/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("robots.txt", robots_txt),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Toutes les autres adresses sont gérées par l'arbre de pages Wagtail
urlpatterns += [path("", include(wagtail_urls))]
