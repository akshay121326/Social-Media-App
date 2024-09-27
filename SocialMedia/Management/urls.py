from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FriendshipManagement,BlockViewSet

router = DefaultRouter()

router.register('friendshipmanagement',FriendshipManagement,basename='friendshipmanagement')
router.register('blockuser',BlockViewSet,basename='blockuser')

urlpatterns = [

] + router.urls