import os
import logging
import uuid
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, FormView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import VideoUploadForm, TextInputForm, VoiceUploadForm, SessionForm, GestureSearchForm
from .models import GestureSession, HandGesture, TextToSign, VoiceToSign, SystemLog
# Lazy imports to avoid loading heavy libraries during startup
# from .video_processing import process_gesture_video_async, process_text_to_sign_async, process_voice_to_sign_async

logger = logging.getLogger(__name__)

# Global variables to manage recording state (for backward compatibility)
predicted_texts = []
Refresh = False
current_vid = 'background.mp4'
translated_texts = ''
Refresh_txt = False


# Video path mappings for gesture types
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


class IndexView(TemplateView):
    """Main landing page view"""
    template_name = 'video_app/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any context data needed for the index page
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'video_app/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any context data needed for the about page
        return context


class SessionListView(LoginRequiredMixin, ListView):
    """View for listing gesture sessions"""
    model = GestureSession
    template_name = 'video_app/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        return GestureSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')


class SessionDetailView(LoginRequiredMixin, DetailView):
    """View for displaying session details"""
    model = GestureSession
    template_name = 'video_app/session_detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return GestureSession.objects.filter(user=self.request.user)


class SessionCreateView(LoginRequiredMixin, FormView):
    """View for creating new gesture sessions"""
    form_class = SessionForm
    template_name = 'video_app/session_create.html'
    success_url = reverse_lazy('video_app:session_list')
    
    def form_valid(self, form):
        session = GestureSession.objects.create(
            user=self.request.user,
            session_name=form.cleaned_data['session_name']
        )
        messages.success(self.request, f'Session "{session.session_name}" created successfully!')
        return redirect('video_app:session_detail', pk=session.pk)


class GestureStreamView(TemplateView):
    """View for real-time gesture streaming"""
    template_name = 'video_app/stream.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.kwargs.get('session_id')
        
        if session_id:
            try:
                session = get_object_or_404(GestureSession, id=session_id)
                context['session'] = session
                context['recent_gestures'] = session.gestures.all()[:10]
            except Exception as e:
                logger.error(f"Error loading session {session_id}: {str(e)}")
                messages.error(self.request, "Session not found.")
        
        return context


class ResponseView(TemplateView):
    """Legacy view for response page - shows text-to-sign functionality"""
    template_name = 'video_app/response.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add global variables for backward compatibility
        global predicted_texts, translated_texts, current_vid
        context['predicted_texts'] = predicted_texts
        context['translated_texts'] = translated_texts
        context['current_vid'] = current_vid
        
        # Add video URL if available
        if current_vid and current_vid != 'background.mp4':
            context['video_url'] = self.request.scheme + '://' + self.request.get_host() + '/media/' + current_vid
        
        return context


class StreamView(TemplateView):
    """Legacy view for stream page - shows hand detection"""
    template_name = 'video_app/stream.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add global variables for backward compatibility
        global predicted_texts, translated_texts, current_vid
        context['predicted_texts'] = predicted_texts
        context['translated_texts'] = translated_texts
        context['current_vid'] = current_vid
        
        # Add video URL if available
        if current_vid and current_vid != 'background.mp4':
            context['video'] = self.request.scheme + '://' + self.request.get_host() + '/media/' + current_vid
        else:
            context['video'] = self.request.scheme + '://' + self.request.get_host() + '/media/' + 'background.mp4'
        
        return context

class VideoUploadView(FormView):
    """View for uploading gesture videos"""
    form_class = VideoUploadForm
    template_name = 'video_app/upload.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        try:
            video_file = form.cleaned_data['video']
            
            print(f"🔍 [DEBUG] Video upload received:")
            print(f"   - File name: {video_file.name}")
            print(f"   - File size: {video_file.size} bytes")
            print(f"   - Content type: {video_file.content_type}")
            
            # Save file temporarily
            file_path = default_storage.save(
                f'temp/{video_file.name}',
                ContentFile(video_file.read())
            )
            
            print(f"🔍 [DEBUG] Video saved to: {file_path}")
            
            # Get the full path for processing
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            print(f"🔍 [DEBUG] Full path for processing: {full_path}")
            
            # Actually process the video using the working function
            from .video_processing import prepare_video
            print(f"🔍 [DEBUG] Starting video processing...")
            
            result = prepare_video(full_path)
            print(f"🔍 [DEBUG] Video processing result: {result}")
            
            if result:
                # Update global variables for backward compatibility
                global predicted_texts, Refresh
                predicted_texts.append(result)
                Refresh = True
                
                return JsonResponse({
                    'statue': True,
                    'text': result,
                    'success': True,
                    'message': 'Video processed successfully',
                    'file_path': file_path
                })
            else:
                return JsonResponse({
                    'statue': False,
                    'text': 'Not recognized gesture',
                    'success': False,
                    'error': 'No gesture detected'
                })
            
        except Exception as e:
            print(f"❌ [DEBUG] Error uploading video: {str(e)}")
            logger.error(f"Error uploading video: {str(e)}")
            return JsonResponse({
                'statue': False,
                'text': 'Error processing video',
                'success': False,
                'error': 'Failed to upload video'
            }, status=500)
    
    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class StreamVideoUploadView(View):
    """API view for uploading videos from stream page (supports webm format)"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            print(f"🔍 [DEBUG] StreamVideoUploadView POST request received")
            print(f"🔍 [DEBUG] Request FILES: {list(request.FILES.keys())}")
            print(f"🔍 [DEBUG] Request POST: {list(request.POST.keys())}")
            
            # Check if video file is present
            if 'video' not in request.FILES:
                print(f"❌ [DEBUG] No video file in request.FILES")
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'No video file provided'
                }, status=400)
            
            video_file = request.FILES['video']
            
            print(f"🔍 [DEBUG] Stream video upload received:")
            print(f"   - File name: {video_file.name}")
            print(f"   - File size: {video_file.size} bytes")
            print(f"   - Content type: {video_file.content_type}")
            
            # Validate file size (max 50MB)
            if video_file.size > 50 * 1024 * 1024:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Video file too large (max 50MB)'
                }, status=400)
            
            # Save file temporarily with proper extension
            file_extension = os.path.splitext(video_file.name)[1].lower()
            if not file_extension:
                # Default to .webm if no extension
                file_extension = '.webm'
            
            # Ensure we have a valid extension
            if file_extension not in ['.webm', '.mp4', '.avi', '.mov']:
                file_extension = '.webm'
            
            temp_filename = f'hand-detection-video_{uuid.uuid4().hex[:8]}{file_extension}'
            
            # Reset file pointer to beginning
            video_file.seek(0)
            
            file_path = default_storage.save(
                f'temp/{temp_filename}',
                ContentFile(video_file.read())
            )
            
            print(f"🔍 [DEBUG] Video saved to: {file_path}")
            
            # Get the full path for processing
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            print(f"🔍 [DEBUG] Full path for processing: {full_path}")
            
            # Process the video using the working function
            from .video_processing import prepare_video
            print(f"🔍 [DEBUG] Starting video processing...")
            
            # Check if file exists and is readable
            if not os.path.exists(full_path):
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Video file not found after saving'
                }, status=500)
            
            file_size = os.path.getsize(full_path)
            print(f"🔍 [DEBUG] File size: {file_size} bytes")
            
            if file_size == 0:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Video file is empty'
                }, status=500)
            
            result = prepare_video(full_path)
            print(f"🔍 [DEBUG] Video processing result: {result}")
            
            if result:
                # Update global variables for backward compatibility
                global predicted_texts, Refresh
                predicted_texts.append(result)
                Refresh = True
                
                return JsonResponse({
                    'statue': True,
                    'text': result,
                    'success': True,
                    'message': 'Video processed successfully',
                    'file_path': file_path
                })
            else:
                return JsonResponse({
                    'statue': False,
                    'text': 'Not recognized gesture',
                    'success': False,
                    'error': 'No gesture detected'
                })
            
        except Exception as e:
            print(f"❌ [DEBUG] Error uploading video: {str(e)}")
            logger.error(f"Error uploading video: {str(e)}")
            return JsonResponse({
                'statue': False,
                'text': 'Error processing video',
                'success': False,
                'error': 'Failed to upload video'
            }, status=500)


class TextToSignView(FormView):
    """View for text-to-sign conversion"""
    form_class = TextInputForm
    template_name = 'video_app/text_to_sign.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        try:
            text = form.cleaned_data['text_input']
            print(f"🔍 [DEBUG] TextToSignView form_valid received: {text}")
            session_id = self.kwargs.get('session_id', str(uuid.uuid4()))
            
            # Process text to sign using the working function
            video_path = process_text(text)
            if video_path:
                # Update global variables for backward compatibility
                global translated_texts, Refresh_txt, current_vid
                translated_texts = text
                current_vid = 'concatenated_video.mp4'
                Refresh_txt = True
                
                last_video_path = self.request.scheme + '://' + self.request.get_host() + '/media/' + 'concatenated_video.mp4'
                print(f"🔍 [DEBUG] TextToSignView video URL: {last_video_path}")
                return JsonResponse({
                    'statue': True,
                    'text': text,
                    'videosrc': last_video_path,
                    'success': True,
                    'message': 'Text converted successfully'
                })
            else:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Failed to process text'
                })
            
        except Exception as e:
            logger.error(f"Error converting text to sign: {str(e)}")
            return JsonResponse({
                'statue': False,
                'success': False,
                'error': 'Failed to convert text to sign'
            }, status=500)
    
    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class VoiceToSignView(FormView):
    """View for voice-to-sign conversion"""
    form_class = VoiceUploadForm
    template_name = 'video_app/voice_to_sign.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        try:
            voice_file = form.cleaned_data['voice_note']
            session_id = self.kwargs.get('session_id', str(uuid.uuid4()))
            
            # Save file temporarily
            file_path = default_storage.save(
                f'temp/{voice_file.name}',
                ContentFile(voice_file.read())
            )
            
            # Process voice to sign (this would be done asynchronously)
            # For now, return a placeholder response
            return JsonResponse({
                'success': True,
                'message': 'Voice converted successfully',
                'transcribed_text': 'Transcribed text placeholder',
                'video_url': '/media/placeholder_voice_to_sign.mp4'
            })
            
        except Exception as e:
            logger.error(f"Error converting voice to sign: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to convert voice to sign'
            }, status=500)
    
    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class StreamVoiceToSignView(View):
    """API view for voice-to-sign conversion from stream page (supports webm format)"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Check if voice file is present
            if 'voiceNote' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No voice file provided'
                }, status=400)
            
            voice_file = request.FILES['voiceNote']
            
            # Validate file size (max 25MB)
            if voice_file.size > 25 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'Voice file too large (max 25MB)'
                }, status=400)
            
            # Save file temporarily with proper extension
            file_extension = os.path.splitext(voice_file.name)[1].lower()
            if not file_extension:
                # Default to .webm if no extension
                file_extension = '.webm'
            
            # Ensure we have a valid extension
            if file_extension not in ['.webm', '.wav', '.mp3', '.m4a']:
                file_extension = '.webm'
            
            temp_filename = f'voice-note_{uuid.uuid4().hex[:8]}{file_extension}'
            
            # Reset file pointer to beginning
            voice_file.seek(0)
            
            file_path = default_storage.save(
                f'temp/{temp_filename}',
                ContentFile(voice_file.read())
            )
            
            # Get the full path for processing
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Process voice to text using speech recognition
            try:
                import speech_recognition as sr
                from pydub import AudioSegment
                
                # Convert audio file to wav format for speech recognition
                audio_file_path = os.path.join(settings.MEDIA_ROOT, f'temp/converted_audio_{uuid.uuid4().hex[:8]}.wav')
                audio = AudioSegment.from_file(full_path)
                audio.export(audio_file_path, format="wav")
                
                # Perform speech recognition
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_file_path) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                    spoken_text = recognizer.recognize_google(audio_data, language="ar")
                
                # Process the recognized text to sign language
                video_path = process_text(spoken_text)
                if video_path:
                    # Update global variables for backward compatibility
                    global translated_texts, Refresh_txt, current_vid
                    translated_texts = spoken_text
                    current_vid = 'concatenated_video.mp4'
                    Refresh_txt = True
                    
                    # Create the video URL for the frontend
                    video_url = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
                    
                    # Clean up temporary files
                    try:
                        os.remove(full_path)
                        os.remove(audio_file_path)
                    except:
                        pass
                    
                    return JsonResponse({
                        'statue': True,
                        'text': spoken_text,
                        'videosrc': video_url,
                        'success': True,
                        'message': 'Voice converted successfully',
                        'file_path': file_path
                    })
                else:
                    return JsonResponse({
                        'statue': False,
                        'success': False,
                        'error': 'Failed to process recognized text'
                    })
                    
            except sr.UnknownValueError:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Could not understand audio'
                })
            except sr.RequestError as e:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': f'Could not request results; {e}'
                })
            except Exception as e:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': f'Failed to process voice: {str(e)}'
                })
            
        except Exception as e:
            print(f"❌ [DEBUG] Error processing voice: {str(e)}")
            logger.error(f"Error processing voice: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to process voice file'
            }, status=500)


class StreamTextToSignView(View):
    """API view for text-to-sign conversion from stream page"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Get text input from POST data
            text_input = request.POST.get('text_input', '').strip()
            
            if not text_input:
                return JsonResponse({
                    'success': False,
                    'error': 'No text provided'
                }, status=400)
            
            # Process text to sign using the working function
            video_path = process_text(text_input)
            if video_path:
                # Update global variables for backward compatibility
                global translated_texts, Refresh_txt, current_vid
                translated_texts = text_input
                current_vid = 'concatenated_video.mp4'
                Refresh_txt = True
                
                # Create the video URL for the frontend
                video_url = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
                
                return JsonResponse({
                    'statue': True,
                    'text': text_input,
                    'videosrc': video_url,
                    'success': True,
                    'message': 'Text converted to sign language successfully',
                    'input_text': text_input
                })
            else:
                return JsonResponse({
                    'statue': False,
                    'success': False,
                    'error': 'Failed to process text'
                })
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to process text'
            }, status=500)

class GestureListView(LoginRequiredMixin, ListView):
    """View for listing gestures with search functionality"""
    model = HandGesture
    template_name = 'video_app/gesture_list.html'
    context_object_name = 'gestures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HandGesture.objects.filter(session__user=self.request.user)
        
        # Apply search filters
        search_query = self.request.GET.get('search_query')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if search_query:
            queryset = queryset.filter(
                Q(gesture_type__icontains=search_query) |
                Q(session__session_name__icontains=search_query)
            )
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = GestureSearchForm(self.request.GET)
        return context


class GestureDetailView(LoginRequiredMixin, DetailView):
    """View for displaying gesture details"""
    model = HandGesture
    template_name = 'video_app/gesture_detail.html'
    context_object_name = 'gesture'
    
    def get_queryset(self):
        return HandGesture.objects.filter(session__user=self.request.user)


class APIViewMixin:
    """Mixin for API views with common functionality"""
    
    def handle_exception(self, e, message="An error occurred"):
        logger.error(f"{message}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': message
        }, status=500)

# API Views for WebSocket integration
class GestureAPIView(APIViewMixin, View):
    """API view for gesture processing via WebSocket"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, session_id):
        """Process gesture video via API"""
        try:
            if 'video' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No video file provided'
                }, status=400)
            
            video_file = request.FILES['video']
            session = get_object_or_404(GestureSession, id=session_id)
            
            print(f"🔍 [DEBUG] API Video upload received:")
            print(f"   - File name: {video_file.name}")
            print(f"   - File size: {video_file.size} bytes")
            print(f"   - Session ID: {session_id}")
            
            # Save video file
            file_path = default_storage.save(
                f'gesture_videos/{session_id}/{video_file.name}',
                ContentFile(video_file.read())
            )
            
            print(f"🔍 [DEBUG] Video saved to: {file_path}")
            
            # Get the full path for processing
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            print(f"🔍 [DEBUG] Full path for processing: {full_path}")
            
            # Actually process the video using the working function
            from .video_processing import prepare_video
            print(f"🔍 [DEBUG] Starting video processing via API...")
            
            result = prepare_video(full_path)
            print(f"🔍 [DEBUG] API Video processing result: {result}")
            
            if result:
                return JsonResponse({
                    'success': True,
                    'message': 'Video processed successfully',
                    'gesture_type': result,
                    'confidence': 0.95,
                    'session_id': session_id,
                    'file_path': file_path
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No gesture detected',
                    'message': 'Not recognized gesture'
                })
            
        except Exception as e:
            print(f"❌ [DEBUG] API Error processing video: {str(e)}")
            return self.handle_exception(e, "Failed to process gesture video")


class TextToSignAPIView(APIViewMixin, View):
    """API view for text-to-sign conversion"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, session_id):
        """Convert text to sign language via API"""
        try:
            data = request.json() if hasattr(request, 'json') else request.POST
            text = data.get('text', '').strip()
            
            if not text:
                return JsonResponse({
                    'success': False,
                    'error': 'No text provided'
                }, status=400)
            
            session = get_object_or_404(GestureSession, id=session_id)
            
            # Create text-to-sign conversion record
            conversion = TextToSign.objects.create(
                session=session,
                input_text=text,
                processing_status='pending'
            )
            
            # Process text (this would trigger WebSocket processing)
            # For now, return a placeholder response
            return JsonResponse({
                'success': True,
                'message': 'Text queued for conversion',
                'conversion_id': str(conversion.id),
                'session_id': session_id
            })
            
        except Exception as e:
            return self.handle_exception(e, "Failed to process text to sign conversion")


class VoiceToSignAPIView(APIViewMixin, View):
    """API view for voice-to-sign conversion"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, session_id):
        """Convert voice to sign language via API"""
        try:
            if 'voice_note' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No audio file provided'
                }, status=400)
            
            voice_file = request.FILES['voice_note']
            session = get_object_or_404(GestureSession, id=session_id)
            
            # Save audio file
            file_path = default_storage.save(
                f'voice_files/{session_id}/{voice_file.name}',
                ContentFile(voice_file.read())
            )
            
            # Create voice-to-sign conversion record
            conversion = VoiceToSign.objects.create(
                session=session,
                audio_file=file_path,
                processing_status='pending'
            )
            
            # Process voice (this would trigger WebSocket processing)
            # For now, return a placeholder response
            return JsonResponse({
                'success': True,
                'message': 'Voice queued for conversion',
                'conversion_id': str(conversion.id),
                'session_id': session_id
            })
            
        except Exception as e:
            return self.handle_exception(e, "Failed to process voice to sign conversion")

# Utility functions for backward compatibility
def search_video(text):
    """Search for video file by text name"""
    video_files = [file for file in os.listdir(settings.MEDIA_ROOT) if file.endswith(".mp4")]
    
    for file in video_files:
        file_name_without_ext = os.path.splitext(file)[0]
        if file_name_without_ext == text:
            video_path = os.path.join(settings.MEDIA_ROOT, file)
            return video_path
    
    return None


def process_text(input_text):
    """Process text to create sign language video"""
    words = input_text.split()
    video_filenames = []
    
    for word in words:
        video_filename = search_video(word)
        if video_filename:
            video_filenames.append(video_filename)
        else:
            letters_videos = []
            letters = []
            for letter in word:
                letter_filename = search_video(letter)
                if letter_filename:
                    letters.append(letter)
                    letters_videos.append(letter_filename)
            
            if letters_videos:
                from .video_processing import concatenate_letters
                new_word_video = concatenate_letters(letters_videos, str(letters))            
                if new_word_video:
                    video_filenames.append(new_word_video)

    if video_filenames:
        from .video_processing import concatenate_videos
        result = concatenate_videos(video_filenames)
        return result
    else:
        return None


# Legacy refresh detection endpoints for backward compatibility
@csrf_exempt
def detect_refresh(request):
    """Legacy endpoint for detecting gesture refresh"""
    global Refresh, predicted_texts
    if Refresh == True:
        text = predicted_texts[-1] if predicted_texts else None
        if text and text in VIDEO_PATHS:
            video_path = VIDEO_PATHS[text]
            if os.path.exists(video_path):
                video_name = VIDEO_PATHS_MEDIA[text]
                last_video_path = request.scheme + '://' + request.get_host() + '/media/' + video_name
                Refresh = False
                return JsonResponse({"statue": True, "text": text, "videosrc": last_video_path}, safe=False)
        return JsonResponse({"statue": False}, safe=False)
    else:
        return JsonResponse({"statue": False}, safe=False)


@csrf_exempt
def detect_refresh_txt(request):
    """Legacy endpoint for detecting text refresh"""
    global Refresh_txt, translated_texts
    if Refresh_txt == True:
        last_video_path = request.scheme + '://' + request.get_host() + '/media/' + 'concatenated_video.mp4'
        Refresh_txt = False
        return JsonResponse({"statue": True, "text": translated_texts, "videosrc": last_video_path}, safe=False)
    else:
        return JsonResponse({"statue": False}, safe=False)

