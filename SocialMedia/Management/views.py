from AuthApp.mixins import ModelViewsetMixin
from .models import *
from rest_framework.decorators import action
from rest_framework import status,views
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import *
from .listserializers import *
from django.db.models import Value,F,Q,When,Case
from AuthApp.throttlers import CustomUserThrottle
from auditlog.models import LogEntry


class FriendshipManagement(ModelViewsetMixin):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    search_fields = ['email','first_name','last_name']
    action_serializer = {
        'show_requests':FriendRequestListSerializer,
        'block_user':BlockSerializer,
        'friend_list':FriendListSerializer,
        'sent_requests':FriendListSerializer
    }

    def get_ordering(self):
        print(f"\033[36m get_ordering called XXXXX\033[0m")
        match self.action:
            case 'friend_list':
                return ['-id','id','first_name','-first_name','last_name','-last_name']
            case 'show_requests':
                return ['-created_at','first_name','-first_name','last_name','-last_name']
            case 'sent_requests':
                return ['-senton','senton','first_name','-first_name','last_name','-last_name']
        return super().get_ordering()

    def get_search_fields(self):
        print(f"\033[36m get_search_fields called XXXXX\033[0m")
        match self.action:
            case 'friend_list':
                return ['first_name','last_name']
            case 'show_requests':
                return ['first_name','last_name']
            case 'friend_list':
                return ['first_name','last_name']
        return super().get_ordering()

    def get_queryset(self):
        if self.action == 'show_requests':
            return FriendRequest.objects.filter(receiver=self.request.user.id)
        elif self.action == 'friend_list':
            return User.objects.filter(
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
        elif self.action == 'sent_requests':
            return User.objects.filter(
                received_requests__sender = self.request.user.id
            ).annotate(
                status = Case(
                    When(
                        received_requests__status = 'A',
                        then = Value('Accepted')
                    ),
                    When(
                        received_requests__status = 'P',
                        then = Value('Pending')
                    ),
                    When(
                        received_requests__status = 'A',
                        then = Value('Cancelled')
                    ),
                    default=Value(''),
                    output_field=models.CharField()
                ),
                senton = F('received_requests__created_at')
            )
        return super().get_queryset()

    @action(detail=True,methods=['put'],throttle_classes=[CustomUserThrottle])
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
    
    def get_paginated_response_data(self, request, queryset):
        """
        Handles filtering, pagination, and serialization of the queryset.
        Used for Listing of: 
            1. sent requests 2. Friends List 3. All recieved request
        """
        filtered_queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(filtered_queryset)
        serializer = self.get_serializer(page, many=True) if page is not None else self.get_serializer(filtered_queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False,methods=['get'])
    def show_requests(self,request):
        queryset = self.get_queryset()
        return self.get_paginated_response_data(request=request,queryset=queryset)

    @action(detail=False,methods=['get'])
    def sent_requests(self,request,):
        queryset = self.get_queryset()
        return self.get_paginated_response_data(request=request,queryset=queryset)
    
    @action(detail=False,methods=['get'])
    def friend_list(self, request):
        queryset = self.get_queryset()
        return self.get_paginated_response_data(request=request,queryset=queryset)



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


class ActivityTrackView(views.APIView):
    serializer_class = None

    def get(self,request):
        user = request.user.id
        queryset = LogEntry.objects.filter(actor=user)
        print(f"\033[34m queryset:{queryset}\033[0m")
        return Response(data={'result':'succes'},status=status.HTTP_200_OK)
