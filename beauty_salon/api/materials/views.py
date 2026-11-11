from rest_framework import viewsets

from .models import Material
from .serializers import MaterialSerializer


class MaterialView(viewsets.ModelViewSet):
    """CRUD для материалов"""

    serializer_class = MaterialSerializer
    queryset = Material.objects.all()
