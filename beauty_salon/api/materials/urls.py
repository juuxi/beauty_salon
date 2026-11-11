from rest_framework import routers

from .views import MaterialView

router = routers.DefaultRouter()
router.register('materials', MaterialView, 'materials')

urlpatterns = router.urls
