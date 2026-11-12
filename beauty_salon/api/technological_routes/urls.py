from rest_framework import routers

from .views import TechnologicalOperationView, TypicalTechnologicalRouteView

router = routers.DefaultRouter()
router.register(
    'technological_operations',
    TechnologicalOperationView,
    'technological_operations',
)
router.register(
    'typical_technological_routes',
    TypicalTechnologicalRouteView,
    'typical_technological_routes',
)

urlpatterns = router.urls
