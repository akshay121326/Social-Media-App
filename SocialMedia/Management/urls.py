from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FriendshipManagement,BlockViewSet,ActivityTrackView

router = DefaultRouter()

router.register('friendshipmanagement',FriendshipManagement,basename='friendshipmanagement')
router.register('blockuser',BlockViewSet,basename='blockuser')

urlpatterns = [
    path('activitytrack/',ActivityTrackView.as_view(),name='activitytrack_url')
] + router.urls