from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Video

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source="uploaded_by.username", read_only=True)
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "description",
            "file_url",
            "thumbnail_url",
            "uploaded_by",
            "created_at",
            "updated_at",
            "views",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return ""

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        if obj.thumbnail:
            return obj.thumbnail.url
        return ""


class VideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id", "title", "description", "file", "thumbnail")
