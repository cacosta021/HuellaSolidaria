from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.listado, name="list"),
    path("<slug:slug>/", views.detalle, name="detail"),
]
