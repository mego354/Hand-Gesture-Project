# video_app/forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os


class VideoUploadForm(forms.Form):
    """Form for uploading gesture videos"""
    video = forms.FileField(
        label="Gesture Video",
        help_text="Upload a video file containing hand gestures (MP4, AVI, MOV)",
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/mp4,video/avi,video/quicktime',
            'id': 'video_upload'
        })
    )
    
    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            # Check file size (max 50MB)
            if video.size > 50 * 1024 * 1024:
                raise ValidationError("Video file is too large. Maximum size is 50MB.")
            
            # Check file extension
            ext = os.path.splitext(video.name)[1].lower()
            if ext not in ['.mp4', '.avi', '.mov']:
                raise ValidationError("Unsupported file format. Please upload MP4, AVI, or MOV files.")
        
        return video


class TextInputForm(forms.Form):
    """Form for text-to-sign conversion"""
    text_input = forms.CharField(
        label="Text to Convert",
        help_text="Enter text to convert to sign language",
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter text here to convert to sign language...',
            'id': 'text_input',
            'rows': 3,
            'maxlength': 500
        }),
        error_messages={
            'required': 'Please enter some text to convert.',
            'max_length': 'Text is too long. Maximum 500 characters allowed.'
        }
    )
    
    def clean_text_input(self):
        text = self.cleaned_data.get('text_input')
        if text:
            # Remove extra whitespace
            text = text.strip()
            if not text:
                raise ValidationError("Text cannot be empty.")
            
            # Check for minimum length
            if len(text) < 2:
                raise ValidationError("Text must be at least 2 characters long.")
        
        return text


class VoiceUploadForm(forms.Form):
    """Form for voice-to-sign conversion"""
    voice_note = forms.FileField(
        label="Voice Recording",
        help_text="Upload an audio file (WAV, MP3, M4A)",
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'm4a'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/wav,audio/mpeg,audio/mp4',
            'id': 'voice_upload'
        })
    )
    
    def clean_voice_note(self):
        voice_file = self.cleaned_data.get('voice_note')
        if voice_file:
            # Check file size (max 25MB)
            if voice_file.size > 25 * 1024 * 1024:
                raise ValidationError("Audio file is too large. Maximum size is 25MB.")
            
            # Check file extension
            ext = os.path.splitext(voice_file.name)[1].lower()
            if ext not in ['.wav', '.mp3', '.m4a']:
                raise ValidationError("Unsupported audio format. Please upload WAV, MP3, or M4A files.")
        
        return voice_file


class SessionForm(forms.Form):
    """Form for creating/editing gesture sessions"""
    session_name = forms.CharField(
        label="Session Name",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter session name...',
            'id': 'session_name'
        }),
        error_messages={
            'required': 'Please enter a session name.',
            'max_length': 'Session name is too long. Maximum 100 characters allowed.'
        }
    )
    
    def clean_session_name(self):
        name = self.cleaned_data.get('session_name')
        if name:
            name = name.strip()
            if not name:
                raise ValidationError("Session name cannot be empty.")
        
        return name


class GestureSearchForm(forms.Form):
    """Form for searching gestures"""
    search_query = forms.CharField(
        label="Search Gestures",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by gesture type or date...',
            'id': 'search_query'
        })
    )
    
    date_from = forms.DateField(
        label="From Date",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'date_from'
        })
    )
    
    date_to = forms.DateField(
        label="To Date",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'date_to'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("From date cannot be later than to date.")
        
        return cleaned_data
