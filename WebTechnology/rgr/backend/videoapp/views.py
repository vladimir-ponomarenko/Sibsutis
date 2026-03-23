from rest_framework import generics, permissions
from .models import Video
from .serializers import UserSerializer, VideoSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class VideoListCreateView(generics.ListCreateAPIView):
    queryset = Video.objects.order_by('-uploaded_at')
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=400)


# videoapp/views.py
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Video
from .serializers import VideoSerializer
from rest_framework.permissions import IsAuthenticated

class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.generics import RetrieveAPIView
from .models import Video
from .serializers import VideoSerializer
from django.http import HttpResponse
import base64

class VideoDetailView(RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


def thumbnail_view(request, pk):
    """Return a simple placeholder thumbnail to keep the UI consistent."""
    transparent_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
        "ASsJTYQAAAAASUVORK5CYII="
    )
    data = base64.b64decode(transparent_png)
    return HttpResponse(data, content_type="image/png")
