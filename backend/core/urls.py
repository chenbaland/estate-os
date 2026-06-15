from django.urls import path

from core import views

urlpatterns = [
    path("", views.HealthCheckView.as_view(), name="health-check"),
]
