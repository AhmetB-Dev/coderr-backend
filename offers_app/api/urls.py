from rest_framework.routers import DefaultRouter

from .views import OfferViewSet


router = DefaultRouter()
router.register("offers", OfferViewSet, basename="offer")

urlpatterns = router.urls
