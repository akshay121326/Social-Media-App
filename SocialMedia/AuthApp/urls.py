from django.urls import path
from .views import UserViewSet
from rest_framework.routers import DefaultRouter
from .views import LoginView,LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

router = DefaultRouter()
router.register('user',UserViewSet,basename='user')

urlpatterns = [
    path('token/',LoginView.as_view(),name='login_url'),
    path('logout/',LogoutView.as_view(),name='logout_url'),
    path('refresh/token/',TokenRefreshView.as_view())
] + router.urls