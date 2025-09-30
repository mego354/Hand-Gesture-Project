# video_app/urls.py
from django.urls import path, include
from . import views

app_name = 'video_app'

urlpatterns = [
    # Main views
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<uuid:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<uuid:session_id>/stream/', views.GestureStreamView.as_view(), name='gesture_stream'),
    
    # Legacy views for backward compatibility
    path('response/', views.ResponseView.as_view(), name='response'),
    path('stream/', views.StreamView.as_view(), name='stream'),
    
    # Gesture views
    path('gestures/', views.GestureListView.as_view(), name='gesture_list'),
    path('gestures/<uuid:pk>/', views.GestureDetailView.as_view(), name='gesture_detail'),
    
    # Upload views
    path('upload/', views.VideoUploadView.as_view(), name='upload'),
    path('stream-upload/', views.StreamVideoUploadView.as_view(), name='stream_upload'),
    path('text-to-sign/', views.TextToSignView.as_view(), name='text_to_sign'),
    path('stream-text-to-sign/', views.StreamTextToSignView.as_view(), name='stream_text_to_sign'),
    path('upload_text/', views.StreamTextToSignView.as_view(), name='upload_text'),  # Legacy compatibility
    path('voice-to-sign/', views.VoiceToSignView.as_view(), name='voice_to_sign'),
    path('stream-voice-to-sign/', views.StreamVoiceToSignView.as_view(), name='stream_voice_to_sign'),
    path('upload_voice/', views.StreamVoiceToSignView.as_view(), name='upload_voice'),  # Legacy compatibility
    
    # Legacy refresh detection endpoints
    path('detect_refresh/', views.detect_refresh, name='detect_refresh'),
    path('detect_refresh_txt/', views.detect_refresh_txt, name='detect_refresh_txt'),
    
    # API endpoints for WebSocket integration
    path('api/sessions/<uuid:session_id>/gestures/', views.GestureAPIView.as_view(), name='api_gesture'),
    path('api/sessions/<uuid:session_id>/text-to-sign/', views.TextToSignAPIView.as_view(), name='api_text_to_sign'),
    path('api/sessions/<uuid:session_id>/voice-to-sign/', views.VoiceToSignAPIView.as_view(), name='api_voice_to_sign'),
]
