from rest_framework import views,viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt import serializers
from .serializers import UserSignupSerializer,UpdatePasswordSerializer,UserSerializer
from .listserializers import UserListSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .pagenations import CustomPagination
from .filters import UserFilter
from django_filters import rest_framework as filters
from .mixins import ModelViewsetMixin
from django.db.models import Q

User = get_user_model()


class UserViewSet(ModelViewsetMixin):
    """ User Sigup/User Resgistration View """
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    action_serializer = {'list':UserListSerializer,}
    search_fields = ['email','first_name','last_name']

    def get_queryset(self):
        if self.action == 'list':
            # Exclude people who blocked you and People whom I have blocked.
            self.queryset = User.objects.exclude(
                Q(blocker__blocked=self.request.user.id)|Q(blocked__blocker=self.request.user.id)
            ).distinct()
        return super().get_queryset()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def create(self,request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data={'message':'user created successfully !!!'},status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=['put'],)
    def update_password(self,request,pk=None):
        user = get_object_or_404(User,id=pk)
        serializer = UpdatePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            oldpassword = serializer.validated_data['old_password']
            newpassword = serializer.validated_data['new_password']
            if not user.check_password(oldpassword):
                return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(newpassword)
            user.save()
            return Response(data={'message':'Password Updated successfully !!!'},status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self,request,pk=None):
        instance = User.objects.get(id=pk)
        serializer = UserSerializer(instance=instance,data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data={'message':'User updated successfully !!!'},status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_200_OK)
    

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        username = request.data.get('username',None)
        email = request.data.get('email',None)
        password = request.data.get('password',None)
        user_kwargs = {'username':username} if username else {'email':email} if email else None
        print(f"\033[34m user_kwargs:{user_kwargs}\033[0m")
        if user_kwargs:
            user = get_object_or_404(User,**user_kwargs)
            username = user.username
            auth_user = authenticate(username=username,password=password)
            if auth_user is not None:
                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token
                http_response = {
                    'refresh':str(refresh_token),
                    'access':str(access_token),
                }
                return Response(data=http_response,status=status.HTTP_200_OK)
            return Response(data={'message':'No active account found with the given credentials'},status=status.HTTP_200_OK)
        raise serializers.ValidationError('Username required !!!')





