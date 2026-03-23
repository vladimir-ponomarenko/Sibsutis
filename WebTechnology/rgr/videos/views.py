import mimetypes
import os

from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponse, Http404
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Video
from .serializers import RegisterSerializer, VideoCreateSerializer, VideoSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return VideoCreateSerializer
        return VideoSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["get"], url_path="stream", permission_classes=[permissions.AllowAny])
    def stream(self, request, pk=None):
        video = self.get_object()
        video_path = video.file.path
        if not os.path.exists(video_path):
            raise Http404("Video not found")

        range_header = request.headers.get("Range", "")
        content_type, _ = mimetypes.guess_type(video_path)
        content_type = content_type or "application/octet-stream"

        if range_header:
            try:
                units, range_spec = range_header.split("=")
                if units != "bytes":
                    return HttpResponse(status=416)
                start_str, end_str = range_spec.split("-")
                file_size = os.path.getsize(video_path)
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                end = min(end, file_size - 1)
                if start > end:
                    return HttpResponse(status=416)
                length = end - start + 1

                with open(video_path, "rb") as video_file:
                    video_file.seek(start)
                    data = video_file.read(length)

                response = HttpResponse(
                    data,
                    status=206,
                    content_type=content_type,
                )
                response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
                response["Accept-Ranges"] = "bytes"
                response["Content-Length"] = str(length)
                video.views = video.views + 1
                video.save(update_fields=["views"])
                return response
            except (ValueError, OSError):
                return HttpResponse(status=416)

        video.views = video.views + 1
        video.save(update_fields=["views"])
        return FileResponse(open(video_path, "rb"), content_type=content_type)
