import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .forms import VideoUploadForm
from .video_processing import predict_single_action, prepare_video
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
# from .models import Room

# Global variables to manage recording state
i = 41
predicted_texts = []
Refresh = False

VIDEO_PATHS = {
    'السلام عليكم': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video1.mp4'),
    'مع السلامه': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video2.mp4'),
    'كيف الحال': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video3.mp4'),
    'مهندس': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video4.mp4')
}
VIDEO_PATHS_MEDIA = {
    'السلام عليكم': 'video1.mp4',
    'مع السلامه': 'video2.mp4',
    'كيف الحال': 'video3.mp4',
    'مهندس': 'video4.mp4'
}

def index(request):
    if request.method == 'GET':
        return render(request, 'video_app/index.html')

@csrf_exempt
def stream(request):
    if request.method == 'GET':
        predicted_texts_reversed = reversed(predicted_texts)
        return render(request, 'video_app/stream.html', {"texts": predicted_texts_reversed})

def response(request):
    global predicted_texts
    predicted_texts_reversed = reversed(predicted_texts)

    try:
        text = predicted_texts[-1]  # Uncomment if you want to use the last predicted text
        if text in VIDEO_PATHS:
            video_name = VIDEO_PATHS_MEDIA[text]
            last_video_path = request.scheme + '://' + request.get_host() + '/media/' + video_name

            return render(request, 'video_app/response.html',{
                'predicted_texts': predicted_texts_reversed,
                'video_url': last_video_path
                })
        
        return render(request, 'video_app/response.html',{
            'predicted_texts': predicted_texts_reversed,
            })
    except Exception:
        return render(request, 'video_app/response.html',{
                    'predicted_texts': predicted_texts_reversed,
                    'error': 'Empty',
                    })

@csrf_exempt
def upload(request):
    global predicted_texts, Refresh

    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = request.FILES['video']
            file_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            text = prepare_video(file_path)  # Adjust SEQUENCE_LENGTH as needed
            if text in VIDEO_PATHS:
                video_path = VIDEO_PATHS[text]
                if os.path.exists(video_path):
                    video_name = VIDEO_PATHS_MEDIA[text]
                    last_video_path = request.scheme + '://' + request.get_host() + '/media/' + video_name
                    predicted_texts.append(text)
                    Refresh = True
                    return JsonResponse({"statue":True, "text":text, "videosrc":last_video_path}, safe=False)
                else:
                    latest_video = {'statue': 'Video file does not exist'}
                    return JsonResponse(latest_video)

            return JsonResponse({"statue":False,}, status=400)
        else:
            return JsonResponse({"statue":False}, status=405)
    else:
        form = VideoUploadForm()
    return render(request, 'video_app/upload2.html', {'form': form})


def detect_refresh(request):
    global Refresh, predicted_texts
    if Refresh == True:
        text = predicted_texts[-1]  # Uncomment if you want to use the last predicted text
        if text in VIDEO_PATHS:
            video_path = VIDEO_PATHS[text]
            if os.path.exists(video_path):
                video_name = VIDEO_PATHS_MEDIA[text]
                last_video_path = request.scheme + '://' + request.get_host() + '/media/' + video_name

                Refresh = False
                return JsonResponse({"statue":True, "text":text, "videosrc":last_video_path}, safe=False)
        return JsonResponse({"statue":False}, safe=False)

    else:
        return JsonResponse({"statue":False}, safe=False)
