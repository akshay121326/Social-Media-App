from rest_framework import serializers
from .models import *


class BlockSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Block
        fields = ['blocker','blocked']

class FriendRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False)
    
    class Meta:
        model = FriendRequest
        fields = ['sender','receiver','status' ]