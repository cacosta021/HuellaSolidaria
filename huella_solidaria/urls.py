from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.pages import views as pages_views

from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),

    # HOME (raíz) -> landing
    path("", pages_views.home, name="pages_home"),

    # Apps con prefijo
    path("adopta/", include("apps.adopciones.urls")),
    path(
        "donaciones/",
        include(("apps.donaciones.urls", "donaciones"), namespace="donaciones"),
    ),

    path("blog/", include("apps.blog.urls", namespace="blog")),
    # Páginas estáticas
    path("nosotros/",   TemplateView.as_view(template_name="pages/nosotros.html"),   name="pages_nosotros"),
    path("club-hs/",    TemplateView.as_view(template_name="pages/club_hs.html"),    name="pages_club_hs"),
    path("consultas/",  TemplateView.as_view(template_name="pages/consultas.html"),  name="pages_consultas"),
    path("faq/",        TemplateView.as_view(template_name="pages/faq.html"),        name="pages_faq"),
    path("terminos/",   TemplateView.as_view(template_name="pages/terminos.html"),   name="pages_terminos"),
    path("privacidad/", TemplateView.as_view(template_name="pages/privacidad.html"), name="pages_privacidad"),
]

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

handler404 = "apps.sitio.views.error_404"
handler500 = "apps.sitio.views.error_500"
handler403 = "apps.sitio.views.error_403"
handler400 = "apps.sitio.views.error_400"


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
