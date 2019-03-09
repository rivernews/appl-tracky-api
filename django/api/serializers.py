from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import (
    Address
)
from rest_framework import serializers
from rest_social_auth.serializers import UserJWTSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    For general API endpoint
    """
    class Meta:
        model = get_user_model()
        fields = ('url', 'email', 'first_name', 'last_name')


class SocialAuthUserSerializer(UserJWTSerializer):
    """
    For social login endpoint to decide what to respond to frontend upon login (work with JWT)
    """
    class Meta:
        model = get_user_model()
        exclude = UserJWTSerializer.Meta.exclude + ('uuid', 'username',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ('url', 'uuid', 'place_name', 'country', 'state', 'street', 'full_address', 'zipcode')