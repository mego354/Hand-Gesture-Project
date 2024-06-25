import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .forms import VideoUploadForm, TextInputForm
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment
import speech_recognition as sr
from .video_processing import predict_single_action, prepare_video, concatenate_videos

# Global variables to manage recording state
predicted_texts = []
Refresh = False

current_vid = 'background.mp4'
translated_texts = ''
Refresh_txt = False


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
    global current_vid, translated_texts
    if request.method == 'GET':
        predicted_texts_reversed = reversed(predicted_texts)
        current_vid_path = request.scheme + '://' + request.get_host() + '/media/' + current_vid
        return render(request, 'video_app/stream.html', {"translated_texts":translated_texts, "video": current_vid_path, "texts": predicted_texts_reversed})

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


###########################################################


@csrf_exempt
def upload_text(request):
    global translated_texts, Refresh_txt, current_vid
    if request.method == 'POST':
        form = TextInputForm(request.POST, request.FILES)
        if form.is_valid():
            text_input = form.cleaned_data.get('text_input')
            try:
                video_path = process_text(text_input)
                if video_path:
                    last_video_path = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
                    Refresh_txt = True
                    translated_texts = text_input
                    current_vid = 'concatenated_video.mp4'
                    return JsonResponse({"statue":True, "text":text_input, "videosrc":last_video_path}, safe=False)
            except Exception:
                return JsonResponse({"statue":False,}, safe=False)
        return JsonResponse({"statue":False,}, safe=False)

    else:
        form = TextInputForm()
    return render(request, 'video_app/uploadtext.html', {'form': form})

@csrf_exempt
def upload_voice(request):
    global translated_texts, Refresh_txt, current_vid
    if request.method == 'POST' and request.FILES.get('voiceNote'):
        voice_note = request.FILES['voiceNote']
        file_path = os.path.join(settings.MEDIA_ROOT, 'original_audio.wav')
        audio_file_path = os.path.join(settings.MEDIA_ROOT, 'converted_audio.wav')
        
        # Save the uploaded file to the MEDIA_ROOT directory
        with open(file_path, 'wb') as f:
            for chunk in voice_note.chunks():
                f.write(chunk)
            
        try:
            recognizer = sr.Recognizer()
            audio = AudioSegment.from_file(file_path)
            audio.export(audio_file_path, format="wav")

            with sr.AudioFile(audio_file_path) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
                spoken_text = recognizer.recognize_google(audio_data, language="ar")
            try:
                video_path = process_text(spoken_text)
                if video_path:
                    last_video_path = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
                    Refresh_txt = True
                    translated_texts = spoken_text
                    current_vid = 'concatenated_video.mp4'
                    os.remove(file_path)
                    os.remove(audio_file_path)

                    return JsonResponse({"statue":True, "text":spoken_text, "videosrc":last_video_path}, safe=False)
            except Exception:
                return JsonResponse({"statue":False,}, safe=False)

        except sr.UnknownValueError:
            return JsonResponse({"status": False, "error": "Could not understand audio"})
        except sr.RequestError as e:
            return JsonResponse({"status": False, "error": f"Could not request results; {e}"})
        except Exception as e:
            return JsonResponse({"status": False, "error": str(e)})

    else:
        return JsonResponse({"status": False, "error": "Invalid request"})


def detect_refresh_txt(request):
    global Refresh_txt, translated_texts
    if Refresh_txt == True:
        last_video_path = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
        Refresh_txt = False
        return JsonResponse({"statue":True, "text":translated_texts, "videosrc":last_video_path}, safe=False)

    else:
        return JsonResponse({"statue":False}, safe=False)


def search_video(text):
    video_files = [file for file in os.listdir(settings.MEDIA_ROOT) if file.endswith(".mp4")]
    for file in video_files:
        if os.path.splitext(file)[0] == text:
            return os.path.join(settings.MEDIA_ROOT, file)
    return None

def process_text(input_text):
    words = input_text.split()
    video_filenames = []
    for word in words:
        video_filename = search_video(word)
        if video_filename:
            video_filenames.append(video_filename)
        else:
            word_clips = [VideoFileClip(search_video(char)) for char in word if search_video(char)]
            if word_clips:
                concatenated_clip = concatenate_videoclips(word_clips)
                temp_filename = os.path.join(settings.MEDIA_ROOT, f"{word}.mp4")
                concatenated_clip.write_videofile(temp_filename)
                video_filenames.append(temp_filename)
    if video_filenames:
        return concatenate_videos(video_filenames)
    return None


def translate_voice():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="ar")
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return None
