from rest_framework import serializers
from .models import Post
from django.contrib.auth.models import User


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("slug", "author", "created_at", "updated_at")


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=validated_data.get("password"),
        )
        return user


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
