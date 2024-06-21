# video_app/video_processing.py
import os
import cv2 as cv
import numpy as np
import tensorflow as tf
from django.conf import settings
import mediapipe as mp

# Define the path to the model file
model_path = os.path.join(settings.BASE_DIR, 'video_app', 'models', 'cconvlstm_model___Date_Time_2024_05_04__12_43_00___Loss_0.016002826392650604___Accuracy_1.0.h5')

model = tf.keras.models.load_model(model_path)
# model = 0
CLASSES_LIST = ['السلام عليكم', 'كيف الحال', 'مع السلامه', 'مهندس']
SEQUENCE_LENGTH = 40
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64

i = 1
success = False
def predict_single_action(video_file_path, SEQUENCE_LENGTH):
    # video_file_path = os.path.join(settings.BASE_DIR, 'media', 'z.mp4')
    video_reader = cv.VideoCapture(video_file_path)
    frames_list = []

    video_frames_count = int(video_reader.get(cv.CAP_PROP_FRAME_COUNT))
    skip_frames_window = max(int(video_frames_count / SEQUENCE_LENGTH), 1)

    for frame_counter in range(SEQUENCE_LENGTH):
        video_reader.set(cv.CAP_PROP_POS_FRAMES, frame_counter * skip_frames_window)
        success, frame = video_reader.read()
        # print(success, frame)
        if not success:
            return "error readind the video"
        resized_frame = cv.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        grey_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
        frames_list.append(grey_frame)

    predicted_labels_probabilities = model.predict(np.expand_dims(frames_list, axis=0))[0]
    predicted_label = np.argmax(predicted_labels_probabilities)
    predicted_class_name = CLASSES_LIST[predicted_label]

    video_reader.release()
    return predicted_class_name
##########################################
def prepare_video(video):
    global i, success
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    video_frame_limit = 40  # Number of frames to record
    cap = cv.VideoCapture(video)
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    frame_count = 0
    video_path = os.path.join(settings.MEDIA_ROOT, f'r{i}.mp4')
    videoWriter = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'H264'), 10, (w, h), False)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("not")
            break
        
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

            print(frame_count)
            videoWriter.write(thresh)
            frame_count += 1
            if frame_count >= video_frame_limit:
                videoWriter.release()
                frame_count = 0
                videoWriter = None
                success = True
                break
        else:
            print("pass")
            pass
    if success:
        success = False
        return predict_single_action(video_path, 40)
    else:
        return None
