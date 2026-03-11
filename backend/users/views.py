from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateAPIView
from django.contrib.auth.models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # 恢复使用默认的 update 逻辑，因为我们已经在前端切断了 avatar 数据
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):
    """Upload user avatar via dedicated endpoint"""
    try:
        avatar = request.FILES.get("avatar")
        if not avatar:
            return Response(
                {"error": "No avatar file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if avatar.content_type not in allowed_types:
            return Response(
                {"error": "Only JPEG, PNG, GIF and WebP images are allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if avatar.size > max_size:
            return Response(
                {"error": "File size must be less than 5MB"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user profile avatar
        user_profile = request.user.profile
        user_profile.avatar = avatar
        user_profile.save()

        serializer = UserProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def remove_avatar(request):
    """Remove user avatar and set to default"""
    try:
        user_profile = request.user.profile
        user_profile.avatar = "avatars/default.jpg"
        user_profile.save()

        serializer = UserProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
