from rest_framework_nested import routers

from .views import EnumerationView, ValueView

router = routers.DefaultRouter()
router.register('enumerations', EnumerationView, 'enumerations')

value_router = routers.NestedDefaultRouter(router, r'enumerations', lookup='enumeration')
value_router.register('values', ValueView, 'value')

urlpatterns = router.urls + value_router.urls
