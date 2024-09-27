from rest_framework import serializers
from .models import *


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ['sender','receiver']