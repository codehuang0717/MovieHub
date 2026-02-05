from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        """将avatar字段转换为完整URL"""
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and data.get("avatar"):
            # 确保返回完整的URL
            avatar_path = data["avatar"]
            if avatar_path and not avatar_path.startswith("http"):
                data["avatar"] = request.build_absolute_uri(avatar_path)
        return data


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]
        read_only_fields = ["id"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include username and password")

        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        # 先更新用户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 然后更新profile信息
        if profile_data is not None:
            profile_serializer = UserProfileSerializer(
                instance.profile, data=profile_data, partial=True
            )
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                # 如果profile验证失败，回滚用户信息更新
                instance.refresh_from_db()
                raise serializers.ValidationError(profile_serializer.errors)

        return instance
