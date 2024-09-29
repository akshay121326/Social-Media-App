from rest_framework import serializers
from .models import *
from AuthApp.serializers import UserLookupSerializer

class BlockListSerializer(serializers.ModelSerializer):
    blocked = UserLookupSerializer()

    class Meta:
        model = Block
        fields = ['id','blocked','created_at']

class FriendListSerializer(serializers.ModelSerializer):
    friendship = serializers.DateTimeField(format="%b %d, %Y",required=False)
    status = serializers.CharField(required=False)
    senton = serializers.DateTimeField(format="%b %d, %Y",required=False)

    class Meta:
        model = User
        fields = ['id','first_name','last_name','friendship','status','senton']

class FriendRequestListSerializer(serializers.ModelSerializer):
    sender = UserLookupSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id','sender','status','created_at']