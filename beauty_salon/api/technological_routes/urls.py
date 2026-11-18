from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    'technological_operations',
    views.TechnologicalOperationView,
    'technological_operations',
)
router.register(
    'typical_technological_routes',
    views.TypicalTechnologicalRouteView,
    'typical_technological_routes',
)
router.register('tools', views.ToolView, 'tools')
router.register('professions', views.ProfessionView, 'professions')
router.register('qualifications', views.QualificationView, 'qualifications')

urlpatterns = router.urls
