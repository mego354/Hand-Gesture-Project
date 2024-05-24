import os
import time
from django.conf import settings
from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from .forms import VideoUploadForm
from .video_processing import predict_single_action
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import cv2 as cv
import numpy as np
import mediapipe as mp
import threading
from moviepy.editor import VideoFileClip, AudioFileClip

# Global variables to manage recording state
recording = False
videoWriter = None
frame_count = 0
i = 41
predicted_texts = []

VIDEO_PATHS = {
    'السلام عليكم': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video1.mp4'),
    'مع السلامه': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video2.mp4'),
    'كيف الحال': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video3.mp4'),
    'مهندس': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video4.mp4')
}

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = request.FILES['video']
            file_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            predicted_text = predict_single_action(file_path, 40)  # Adjust SEQUENCE_LENGTH as needed
            return render(request, 'video_app/result.html', {'predicted_text': predicted_text})
        return render(request, 'video_app/result.html', {'predicted_text': "error predicted_text error"})
    else:
        form = VideoUploadForm()
    return render(request, 'video_app/upload.html', {'form': form})

@gzip.gzip_page
def webcam_stream(request):
    global recording, videoWriter, frame_count, i, predicted_texts
    cap = cv.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    SEQUENCE_LENGTH = 40
    video_frame_limit = 40  # Number of frames to record

    def stream_frames():
        global recording, videoWriter, frame_count, i, predicted_texts
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            h, w, c = frame.shape
            mask = np.zeros(frame.shape[:2], dtype="uint8")
            frame = cv.flip(frame, 1)
            imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            thresh = np.zeros_like(frame[:, :, 0])

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    x_max, y_max = 0, 0
                    x_min, y_min = w, h
                    for lm in handLms.landmark:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        if cx > x_max:
                            x_max = cx
                        if cx < x_min:
                            x_min = cx
                        if cy > y_max:
                            y_max = cy
                        if cy < y_min:
                            y_min = cy
                    rect_margin = 16
                    x_min -= rect_margin
                    y_min -= rect_margin
                    x_max += rect_margin
                    y_max += rect_margin
                    cv.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
                    cv.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
                    mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
                    masked = cv.bitwise_and(frame, frame, mask=mask)
                    gray = cv.cvtColor(masked, cv.COLOR_BGR2GRAY)
                    ret, thresh = cv.threshold(gray, 215, 255, cv.THRESH_BINARY_INV)

                # Recording logic
                if recording:
                    if videoWriter is None:
                        video_path = os.path.join(settings.MEDIA_ROOT, f'{i}.mp4')
                        videoWriter = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'H264'), 10, (w, h), False)
                    videoWriter.write(thresh)
                    frame_count += 1
                    if frame_count >= video_frame_limit:
                        videoWriter.release()
                        predicted_text = predict_single_action(video_path, SEQUENCE_LENGTH)
                        predicted_texts.append(predicted_text)
                        i += 1
                        frame_count = 0
                        videoWriter = None
                        recording = False

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + cv.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

    threading.Thread(target=stream_frames).start()
    return StreamingHttpResponse(stream_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def webcam_stream_page(request):
    if request.method == 'POST':
        global recording, predicted_texts
        if 'start' in request.POST:
            recording = True
        elif 'stop' in request.POST:
            recording = False

    return render(request, 'video_app/stream.html', {'predicted_texts': predicted_texts})


        # text = 'predicted_texts[-1]'  # Get the last predicted text dictionary
def get_latest_video(request):
    global predicted_texts
    try:
        text = predicted_texts[-1]  # Uncomment if you want to use the last predicted text
        if text in VIDEO_PATHS:
            video_path = VIDEO_PATHS[text]
            if os.path.exists(video_path):
                return FileResponse(open(video_path, 'rb'), content_type='video/mp4')
            else:
                latest_video = {'error': 'Video file does not exist'}
        else:
            latest_video = {'error': 'Text not found in VIDEO_PATHS'}
    except Exception as e:
        print(e)
        latest_video = {'error': 'An error occurred'}

    # Ensure proper closure of files
    return JsonResponse(latest_video)