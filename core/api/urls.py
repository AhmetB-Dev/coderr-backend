from django.urls import path

from .views import BaseInfoView, HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path(
        "base-info/",
        BaseInfoView.as_view(),
        name="base-info",
    ),
]
