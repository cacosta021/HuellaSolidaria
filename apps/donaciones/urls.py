from django.urls import path
from . import views

app_name = "donaciones"

urlpatterns = [
    path("", views.donar, name="donar"), 
]
