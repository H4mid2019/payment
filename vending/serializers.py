from rest_framework import serializers
from .models import Product, VendingUser
# from django.contrib.auth import get_user_model

class ProductSerializer(serializers.ModelSerializer):
    """serializes data from the model 

    Args:
        serializers (django db model): it gets the django db model named Product
    """
    class Meta:
        model = Product
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VendingUser
        fields = (
            'id',
            'username',
            'password',
            'role',
            'deposit',
            'email',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def create(self, validated_data):
        user = VendingUser(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data["role"],
            deposit=validated_data['deposit']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
