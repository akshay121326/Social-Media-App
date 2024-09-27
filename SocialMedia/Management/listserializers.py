from rest_framework import serializers
from .models import *
from AuthApp.serializers import UserLookupSerializer

class BlockListSerializer(serializers.ModelSerializer):
    blocked = UserLookupSerializer()
    
    class Meta:
        model = Block
        fields = ['id','blocked','created_at']


class FriendRequestListSerializer(serializers.ModelSerializer):
    sender = UserLookupSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id','sender','status','created_at']