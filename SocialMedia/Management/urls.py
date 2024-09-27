from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FriendshipManagement

router = DefaultRouter()

router.register('friendshipmanagement',FriendshipManagement,basename='friendshipmanagement')

urlpatterns = [

] + router.urls