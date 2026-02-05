#!/usr/bin/env python
"""
Debug script to test UserProfile update functionality
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation.settings")
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from users.serializers import UserUpdateSerializer


def test_profile_update():
    print("=== Testing UserProfile Update ===")

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username="testuser",
        defaults={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    if created:
        user.set_password("testpass123")
        user.save()
        print(f"Created new user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")

    # Check user profile
    try:
        profile = user.profile
        print(f"Found profile: {profile}")
        print(f"Current bio: '{profile.bio}'")
        print(f"Current avatar: {profile.avatar}")
    except UserProfile.DoesNotExist:
        print("No profile found for user!")
        return

    # Test serializer with new bio data (exclude avatar for now)
    test_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile": {"bio": "This is a test bio from debug script updated again"},
    }

    print(f"\n=== Testing with data ===")
    print(f"Test data: {test_data}")

    # Test serializer
    serializer = UserUpdateSerializer(user, data=test_data, partial=True)

    print(f"\n=== Serializer Validation ===")
    print(f"Serializer is valid: {serializer.is_valid()}")

    if not serializer.is_valid():
        print(f"Serializer errors: {serializer.errors}")
        return

    print(f"Validated data: {serializer.validated_data}")

    # Save the serializer
    print(f"\n=== Saving Serializer ===")
    try:
        updated_user = serializer.save()
        print(f"Save successful!")
        print(f"Updated bio: '{updated_user.profile.bio}'")
    except Exception as e:
        print(f"Save failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_profile_update()
