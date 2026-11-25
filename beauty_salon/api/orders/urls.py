from rest_framework_nested import routers
from django.urls import path

from .views import (
    EconomicActivitySubjectView,
    OrderView,
    OrderPositionView,
    AddToOrderView,
    CalcSumView,
)

router = routers.DefaultRouter()
router.register('economic_activity_subjects', EconomicActivitySubjectView, 'economic_activity_subjects')
router.register('orders', OrderView, 'orders')

positions_router = routers.NestedDefaultRouter(
    router, r'orders', lookup='order',
)
positions_router.register('positions', OrderPositionView, 'positions')

urlpatterns = router.urls + positions_router.urls + [
    path('orders/add_position/', AddToOrderView.as_view(), name='add-to-order'),
    path('orders/<int:order_id>/sum/', CalcSumView.as_view(), name='calc_sum'),
]
