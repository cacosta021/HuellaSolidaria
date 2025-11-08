from django.urls import path
from . import views

urlpatterns = [
    path("", views.listado, name="adopta_listado"),
    path("wufs/", views.listado_wufs, name="adopta_wufs"),
    path("miaus/", views.listado_miaus, name="adopta_miaus"),
    path("<int:pk>/", views.detalle, name="adopta_detalle"),
    path("api/razas/", views.razas_por_tipo, name="adopta_api_razas"),
    path("<int:pk>/postular/", views.postular, name="adopta_postular"),

]
