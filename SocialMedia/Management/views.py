from AuthApp.mixins import ModelViewsetMixin
from .models import *
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import *
from .listserializers import *


class FriendshipManagement(ModelViewsetMixin):
    queryset = User.objects.all()
    serializer_class = FriendRequestSerializer
    search_fields = ['email','first_name','last_name']
    action_serializer = {
        'show_requests':FriendRequestListSerializer
    }

    def get_queryset(self):
        if self.action == 'show_requests':
            self.queryset = FriendRequest.objects.filter(receiver=self.request.user.id)
        return super().get_queryset()

    @action(detail=True,methods=['put'])
    def send_request(self,request,pk=None):
        receiver = get_object_or_404(User,id=pk)
        serializer = FriendRequestSerializer(data={'receiver':pk,'sender':request.user.id})
        if serializer.is_valid():
            serializer.save()
            return Response(data={'result':'Friends request sent !!!'},status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            unique_together_error = any(
                'already exists' in str(error).lower() or 'unique' in str(error).lower()
                for error in errors.values()
            )
            if unique_together_error:
                return Response(data={'result': 'Friend request already sent!'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,methods=['get'])
    def show_requests(self,request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)


