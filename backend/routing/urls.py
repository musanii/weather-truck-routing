from django.urls import path
from . import views

urlpatterns =[
    path("health/", views.health_check, name="health-check"),
    path("routes/", views.routes_view, name="routes"),
]