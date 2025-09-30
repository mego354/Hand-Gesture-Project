# video_app/video_processing.py
import os
from django.conf import settings

# Try to import heavy dependencies, but don't fail if they're not available
try:
    import cv2 as cv
    import numpy as np
    import mediapipe as mp
    import tensorflow as tf
    
    model_path = os.path.join(settings.BASE_DIR, 'video_app', 'models', 'model.h5')
    model = tf.keras.models.load_model(model_path)
    CLASSES_LIST = ['السلام عليكم', 'كيف الحال', 'مع السلامه', 'مهندس']
    SEQUENCE_LENGTH = 40
    IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
    
    # Set flag to indicate if heavy dependencies are available
    HEAVY_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ [WARNING] Heavy dependencies not available: {e}")
    print("⚠️ [WARNING] Video prediction features will be disabled")
    HEAVY_DEPENDENCIES_AVAILABLE = False

i = 1
success = False

def predict_single_action(video_file_path, SEQUENCE_LENGTH):
    if not HEAVY_DEPENDENCIES_AVAILABLE:
        print("❌ [ERROR] Heavy dependencies not available for video prediction")
        return "error: dependencies not available"
    
    print(f"🔍 [DEBUG] Starting prediction for video: {video_file_path}")
    print(f"🔍 [DEBUG] Sequence length: {SEQUENCE_LENGTH}")
    
    video_reader = cv.VideoCapture(video_file_path)
    if not video_reader.isOpened():
        print(f"❌ [DEBUG] Failed to open video file: {video_file_path}")
        return "error opening the video"
    
    frames_list = []

    video_frames_count = int(video_reader.get(cv.CAP_PROP_FRAME_COUNT))
    video_fps = video_reader.get(cv.CAP_PROP_FPS)
    video_width = int(video_reader.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_reader.get(cv.CAP_PROP_FRAME_HEIGHT))
    
    print(f"🔍 [DEBUG] Video properties:")
    print(f"   - Total frames: {video_frames_count}")
    print(f"   - FPS: {video_fps}")
    print(f"   - Dimensions: {video_width}x{video_height}")
    
    skip_frames_window = max(int(video_frames_count / SEQUENCE_LENGTH), 1)
    print(f"🔍 [DEBUG] Skip frames window: {skip_frames_window}")

    print(f"🔍 [DEBUG] Extracting {SEQUENCE_LENGTH} frames...")
    for frame_counter in range(SEQUENCE_LENGTH):
        frame_position = frame_counter * skip_frames_window
        video_reader.set(cv.CAP_PROP_POS_FRAMES, frame_position)
        success, frame = video_reader.read()
        
        if not success:
            print(f"❌ [DEBUG] Failed to read frame at position {frame_position}")
            video_reader.release()
            return "error reading the video"
        
        resized_frame = cv.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        grey_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
        frames_list.append(grey_frame)
        
        if frame_counter % 10 == 0:  # Print every 10th frame
            print(f"   - Frame {frame_counter}: position {frame_position}, shape: {grey_frame.shape}, min: {grey_frame.min()}, max: {grey_frame.max()}")

    print(f"🔍 [DEBUG] Successfully extracted {len(frames_list)} frames")
    print(f"🔍 [DEBUG] Model input shape: {model.input_shape}")
    
    # Prepare input data
    input_data = np.expand_dims(frames_list, axis=0)
    print(f"🔍 [DEBUG] Input data shape: {input_data.shape}")
    print(f"🔍 [DEBUG] Input data type: {input_data.dtype}")
    print(f"🔍 [DEBUG] Input data range: [{input_data.min()}, {input_data.max()}]")

    print(f"🔍 [DEBUG] Making prediction...")
    predicted_labels_probabilities = model.predict(input_data, verbose=1)[0]
    
    print(f"🔍 [DEBUG] Raw model output shape: {predicted_labels_probabilities.shape}")
    print(f"🔍 [DEBUG] Raw model output: {predicted_labels_probabilities}")
    
    predicted_label = np.argmax(predicted_labels_probabilities)
    predicted_class_name = CLASSES_LIST[predicted_label]
    confidence = float(predicted_labels_probabilities[predicted_label])
    
    print(f"🎯 [DEBUG] Prediction Results:")
    print(f"   - Predicted label index: {predicted_label}")
    print(f"   - Predicted class: {predicted_class_name}")
    print(f"   - Confidence: {confidence:.4f}")
    print(f"   - All probabilities: {predicted_labels_probabilities.tolist()}")

    video_reader.release()
    return predicted_class_name

##########################################
def prepare_video(video):
    if not HEAVY_DEPENDENCIES_AVAILABLE:
        print("❌ [ERROR] Heavy dependencies not available for video processing")
        return None
    
    global success
    print(f"🔍 [DEBUG] Starting prepare_video for: {video}")
    
    try:
        mpHands = mp.solutions.hands
        hands = mpHands.Hands()
        mpDraw = mp.solutions.drawing_utils
        video_frame_limit = 40  # Number of frames to record
        cap = cv.VideoCapture(video)
        
        if not cap.isOpened():
            print(f"❌ [DEBUG] Failed to open video for hand detection: {video}")
            return None
    except Exception as e:
        print(f"❌ [DEBUG] Error initializing video processing: {str(e)}")
        return None
    
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    
    print(f"🔍 [DEBUG] Video properties for hand detection:")
    print(f"   - Dimensions: {w}x{h}")
    print(f"   - FPS: {fps}")
    print(f"   - Total frames: {total_frames}")
    print(f"   - Frame limit: {video_frame_limit}")
    
    frame_count = 0
    video_path = os.path.join(settings.MEDIA_ROOT, 'hand gesture.mp4')
    videoWriter = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'H264'), 10, (w, h), False)
    
    hands_detected_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"🔍 [DEBUG] Reached end of video at frame {frame_count}")
            break
        
        mask = np.zeros(frame.shape[:2], dtype="uint8")
        frame = cv.flip(frame, 1)
        imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        thresh = np.zeros_like(frame[:, :, 0])

        if results.multi_hand_landmarks:
            hands_detected_count += 1
            hands_detected = len(results.multi_hand_landmarks)
            
            if frame_count % 10 == 0:  # Print every 10th frame with hands
                print(f"   - Frame {frame_count}: {hands_detected} hand(s) detected")
            
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

            print(f"🔍 [DEBUG] Frame {frame_count}: Writing processed frame")
            videoWriter.write(thresh)
            frame_count += 1
            if frame_count >= video_frame_limit:
                videoWriter.release()
                frame_count = 0
                videoWriter = None
                success = True
                break
        else:
            if frame_count % 20 == 0:  # Print every 20th frame without hands
                print(f"   - Frame {frame_count}: No hands detected")
            videoWriter.write(thresh)
            frame_count += 1

    cap.release()
    hands.close()
    
    print(f"🔍 [DEBUG] Hand detection completed:")
    print(f"   - Frames processed: {frame_count}")
    print(f"   - Frames with hands: {hands_detected_count}")
    print(f"   - Success: {success}")
    print(f"   - Output video: {video_path}")

    try:
        if success:
            success = False
            print(f"🔍 [DEBUG] Calling predict_single_action with: {video_path}")
            result = predict_single_action(video_path, 40)
            print(f"🎯 [DEBUG] Final result from prepare_video: {result}")
            return result
        else:
            print(f"❌ [DEBUG] No hands detected in video")
            return None
    except Exception as e:
        print(f"❌ [DEBUG] Error in final processing: {str(e)}")
        return None


def concatenate_videos(video_filenames):
    video_clips = [cv.VideoCapture(filename) for filename in video_filenames]
    
    # Get the width, height, and FPS of the first video
    width = int(video_clips[0].get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video_clips[0].get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = video_clips[0].get(cv.CAP_PROP_FPS)
    
    # Create a VideoWriter object
    output_path = os.path.join(settings.BASE_DIR, 'media', 'concatenated_video.mp4')

    # out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'H264'), fps, (width, height), False)

    
    for clip in video_clips:
        while True:
            ret, frame = clip.read()
            if not ret:
                break
            out.write(frame)
        clip.release()
    
    out.release()
    return output_path

def concatenate_letters(letters_filenames, file_name):
    video_clips = [cv.VideoCapture(filename) for filename in letters_filenames]
    
    # Get the width, height, and FPS of the first video
    width = int(video_clips[0].get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video_clips[0].get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = video_clips[0].get(cv.CAP_PROP_FPS)
    
    # Create a VideoWriter object
    output_path = os.path.join(settings.BASE_DIR, 'media', f'{file_name}.mp4')

    # out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'H264'), fps, (width, height), False)

    
    for clip in video_clips:
        while True:
            ret, frame = clip.read()
            if not ret:
                break
            out.write(frame)
        clip.release()
    
    out.release()
    return output_path


# Async wrapper functions for WebSocket compatibility
import asyncio
import tempfile
import uuid
from typing import Dict, Optional

async def process_gesture_video_async(video_data: bytes, session_id: str) -> Dict:
    """
    Async wrapper for gesture video processing
    """
    try:
        print(f"🔍 [DEBUG] process_gesture_video_async called with session_id: {session_id}")
        print(f"🔍 [DEBUG] Video data size: {len(video_data)} bytes")
        
        # Save video data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(video_data)
            temp_video_path = temp_file.name
        
        print(f"🔍 [DEBUG] Saved video to temporary file: {temp_video_path}")
        
        # Process the video using the synchronous function
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, prepare_video, temp_video_path)
        
        print(f"🔍 [DEBUG] prepare_video returned: {result}")
        
        # Clean up temporary file
        try:
            os.unlink(temp_video_path)
            print(f"🔍 [DEBUG] Cleaned up temporary file: {temp_video_path}")
        except:
            pass
        
        if result:
            return {
                "success": True,
                "gesture_type": result,
                "confidence": 0.95,  # Default confidence since original doesn't return it
                "video_url": "/media/hand gesture.mp4"
            }
        else:
            return {"success": False, "error": "Failed to process gesture video"}
            
    except Exception as e:
        print(f"❌ [DEBUG] Exception in process_gesture_video_async: {str(e)}")
        return {"success": False, "error": f"Video processing failed: {str(e)}"}

async def process_text_to_sign_async(text: str, session_id: str) -> Dict:
    """
    Async wrapper for text-to-sign conversion
    """
    try:
        # This would implement the text-to-sign logic
        # For now, return a placeholder
        return {
            "success": True,
            "video_url": "/media/placeholder_text_to_sign.mp4",
            "conversion_id": str(uuid.uuid4())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def process_voice_to_sign_async(audio_data: bytes, session_id: str) -> Dict:
    """
    Async wrapper for voice-to-sign conversion
    """
    try:
        # This would implement the voice-to-sign logic
        # For now, return a placeholder
        return {
            "success": True,
            "transcribed_text": "Transcribed text placeholder",
            "video_url": "/media/placeholder_voice_to_sign.mp4",
            "conversion_id": str(uuid.uuid4())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}