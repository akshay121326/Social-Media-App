from .pagenations import CustomPagination
from rest_framework import viewsets
from rest_framework import permissions, filters
from django_filters.rest_framework import DjangoFilterBackend


class ModelViewsetMixin(viewsets.ModelViewSet):
    """ Viewset Mixins having cutom pagenation class,filtersebackend """
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter]

    def get_serializer_class(self):
        print(f"\033[36m self.action {self.action}\033[0m")
        if hasattr(self,'action_serializer'):
            self.serializer_class = self.action_serializer.get(self.action,self.serializer_class)
        return super().get_serializer_class()