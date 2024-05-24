# video_app/urls.py
from django.urls import path
from .views import upload_video, webcam_stream, webcam_stream_page, get_latest_video, detect_refresh, api_upload_video

urlpatterns = [
    path('upload/', api_upload_video, name='api_upload_video'),
    path('upload_video/', upload_video, name='upload_video'),
    path('webcam_stream/', webcam_stream, name='webcam_stream'),
    path('', webcam_stream_page, name='webcam_stream_page'),
    path('get_latest_video/', get_latest_video, name='get_latest_video'),
    path('detect_refresh/', detect_refresh, name='detect_refresh'),

]
