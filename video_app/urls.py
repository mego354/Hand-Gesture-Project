# video_app/urls.py
from django.urls import path
from .views import index, stream, response, upload, detect_refresh

urlpatterns = [
    path('', index, name='index'),
    path('stream/', stream, name='stream'),
    path('response/', response, name='response'),
    path('upload/', upload, name='upload'),
    path('detect_refresh/', detect_refresh, name='detect_refresh'),

]
