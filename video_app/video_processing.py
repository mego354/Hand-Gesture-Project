# video_app/video_processing.py
import os
import cv2 as cv
import numpy as np
import tensorflow as tf
from django.conf import settings

# Define the path to the model file
model_path = os.path.join(settings.BASE_DIR, 'video_app', 'models', 'cconvlstm_model___Date_Time_2024_05_04__12_43_00___Loss_0.016002826392650604___Accuracy_1.0.h5')

model = tf.keras.models.load_model(model_path)
# model = 0
CLASSES_LIST = ['السلام عليكم', 'كيف الحال', 'مع السلامه', 'مهندس']
SEQUENCE_LENGTH = 40
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64

def predict_single_action(video_file_path, SEQUENCE_LENGTH):
    # video_file_path = os.path.join(settings.BASE_DIR, 'media', 'z.mp4')
    video_reader = cv.VideoCapture(video_file_path)
    frames_list = []

    video_frames_count = int(video_reader.get(cv.CAP_PROP_FRAME_COUNT))
    skip_frames_window = max(int(video_frames_count / SEQUENCE_LENGTH), 1)

    for frame_counter in range(SEQUENCE_LENGTH):
        video_reader.set(cv.CAP_PROP_POS_FRAMES, frame_counter * skip_frames_window)
        success, frame = video_reader.read()
        print(success, frame)
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
