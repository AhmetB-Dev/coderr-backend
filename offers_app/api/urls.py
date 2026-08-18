from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import OfferDetailView, OfferViewSet


router = DefaultRouter()
router.register("offers", OfferViewSet, basename="offer")

urlpatterns = [
    path(
        "offerdetails/<int:pk>/",
        OfferDetailView.as_view(),
        name="offerdetail-detail",
    ),
]

urlpatterns += router.urls
