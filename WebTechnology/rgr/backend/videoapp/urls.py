# videoapp/urls.py
from django.urls import path
from .views import (
    RegisterView,
    VideoListCreateView,
    login_view,
    VideoUploadView,
    VideoDetailView,
    thumbnail_view,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('videos/', VideoListCreateView.as_view(), name='video-list-create'),
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('videos/<int:pk>/thumbnail', thumbnail_view, name='video-thumbnail'),

]
