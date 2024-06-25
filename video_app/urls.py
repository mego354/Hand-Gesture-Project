# video_app/urls.py
from django.urls import path
from .views import index, stream, response, upload, detect_refresh, upload_text, detect_refresh_txt, upload_voice

urlpatterns = [
    path('', index, name='index'),
    path('stream/', stream, name='stream'),
    path('response/', response, name='response'),
    path('upload/', upload, name='upload'),
    path('upload_text/', upload_text, name='upload_text'),
    path('upload_voice/', upload_voice, name='upload_voice'),
    path('detect_refresh/', detect_refresh, name='detect_refresh'),
    path('detect_refresh_txt/', detect_refresh_txt, name='detect_refresh_txt'),

]
