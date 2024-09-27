from rest_framework import serializers
from .models import *
from AuthApp.serializers import UserLookupSerializer


class FriendRequestListSerializer(serializers.ModelSerializer):
    sender = UserLookupSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id','sender','status','created_at']