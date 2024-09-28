from AuthApp.mixins import ModelViewsetMixin
from .models import *
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import *
from .listserializers import *
from django.db.models import Value,F,Q,When,Case,ExpressionWrapper, DurationField
from django.db.models.functions import Now


class FriendshipManagement(ModelViewsetMixin):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    search_fields = ['email','first_name','last_name']
    action_serializer = {
        'show_requests':FriendRequestListSerializer,
        'block_user':BlockSerializer,
        'friend_list':FriendListSerializer
    }

    def get_queryset(self):
        if self.action == 'show_requests':
            self.queryset = FriendRequest.objects.filter(receiver=self.request.user.id)
        elif self.action == 'friend_list':
            self.queryset = User.objects.filter(
                Q(
                    Q(received_requests__sender=self.request.user.id,received_requests__status='A')
                    |Q(sent_requests__receiver=self.request.user.id,sent_requests__status='A')
                )
            ).annotate(
                friendship=Case(
                    When(
                        sent_requests__receiver=self.request.user.id, 
                        sent_requests__status='A',
                        then=F('sent_requests__created_at'),
                    ),
                    When(
                        received_requests__sender=self.request.user.id, 
                        received_requests__status='A',
                        then=F('received_requests__created_at'),
                    ),
                    default=Value(''),
                    output_field=models.DateTimeField()
                )
            )
            print(f"\033[33m self.queryset {self.queryset.values('friendship')}\033[0m")
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
    
    @action(detail=True,methods=['put'])
    def manage_request(self,request,pk=None):
        'Used to accept and reject status'
        data = request.data
        instance = get_object_or_404(FriendRequest,id=pk)
        serializer = self.get_serializer(instance=instance,data=data,partial=True)
        if serializer.is_valid():
            saved_data =serializer.save() 
            match saved_data.status:
                case 'A':
                    return Response(data={'result':'Friend request accepetd !!!'},status=status.HTTP_200_OK)
                case 'P':
                    return Response(data={'result':'Friend request still in pending !!!'},status=status.HTTP_200_OK)
                case 'R':
                    return Response(data={'result':'Friend request rejected !!!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,methods=['get'])
    def show_requests(self,request):
        """List of friend requests"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=False,methods=['get'])
    def friend_list(self,request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset) 
        print(f"\033[33m queryset:{queryset}\033[0m")
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)



class BlockViewSet(ModelViewsetMixin):
    """Maintain blocked user"""
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    action_serializer = {
        'list': BlockListSerializer,
        'block_user':BlockSerializer
    }

    def get_queryset(self):
        if self.action == 'list':
            self.queryset = Block.objects.filter(blocker=self.request.user.id)
        elif self.action == 'block_user':
            self.queryset = Block.objects.filter(blocker=self.request.user.id)
        elif self.action == 'unblock_user':
            self.queryset = Block.objects.filter(blocker=self.request.user.id)
        return super().get_queryset()

    @action(detail=True,methods=['put'])
    def block_user(self,request,pk=None):
        """Used to block user"""
        # block & blocker should not be same.
        if request.user.id == pk:
            raise serializers.ValidationError({'errors':'Cannot block yourself.'})
        # checks user is already blocked or not.
        if self.get_queryset().filter(blocked=pk):
            raise serializers.ValidationError({'error':'User is already blocked'})
        data = {'blocker':request.user.id,'blocked':pk}
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'result':'User blocked successfully'},status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['put'])
    def unblock_user(self,request,pk=None):
        """Used to unblock user"""
        # block & unblocker should not be same.
        if request.user.id == pk:
            raise serializers.ValidationError({'errors':'Cannot unblock yourself.'})
        if not self.get_queryset().filter(blocked=pk):
            raise serializers.ValidationError({'error':'User is already unblocked'})
        data = self.get_queryset().filter(blocked=pk).delete()
        print(data)
        return Response(data={'result':'User unblocked successfully'},status=status.HTTP_200_OK)
        






