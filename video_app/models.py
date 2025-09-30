import os
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class GestureSession(models.Model):
    """Model to track hand gesture recognition sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_name = models.CharField(max_length=100, default="Untitled Session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gesture Session"
        verbose_name_plural = "Gesture Sessions"
    
    def __str__(self):
        return f"Session {self.session_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class HandGesture(models.Model):
    """Model to store recognized hand gestures"""
    GESTURE_TYPES = [
        ('السلام عليكم', 'السلام عليكم'),
        ('مع السلامه', 'مع السلامه'),
        ('كيف الحال', 'كيف الحال'),
        ('مهندس', 'مهندس'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GestureSession, on_delete=models.CASCADE, related_name='gestures')
    gesture_type = models.CharField(max_length=50, choices=GESTURE_TYPES)
    confidence_score = models.FloatField(default=0.0)
    video_file = models.FileField(
        upload_to='gesture_videos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])],
        null=True,
        blank=True
    )
    processed_video = models.FileField(
        upload_to='processed_videos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Hand Gesture"
        verbose_name_plural = "Hand Gestures"
    
    def __str__(self):
        return f"{self.gesture_type} - {self.confidence_score:.2f}"


class TextToSign(models.Model):
    """Model to store text-to-sign language conversions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GestureSession, on_delete=models.CASCADE, related_name='text_conversions')
    input_text = models.TextField()
    output_video = models.FileField(
        upload_to='text_to_sign/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        null=True,
        blank=True
    )
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Text to Sign Conversion"
        verbose_name_plural = "Text to Sign Conversions"
    
    def __str__(self):
        return f"Text: {self.input_text[:50]}... - {self.processing_status}"


class VoiceToSign(models.Model):
    """Model to store voice-to-sign language conversions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GestureSession, on_delete=models.CASCADE, related_name='voice_conversions')
    audio_file = models.FileField(
        upload_to='voice_files/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'm4a'])],
    )
    transcribed_text = models.TextField(null=True, blank=True)
    output_video = models.FileField(
        upload_to='voice_to_sign/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        null=True,
        blank=True
    )
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('transcribing', 'Transcribing'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Voice to Sign Conversion"
        verbose_name_plural = "Voice to Sign Conversions"
    
    def __str__(self):
        return f"Voice: {self.audio_file.name} - {self.processing_status}"


class SystemLog(models.Model):
    """Model to store system logs and errors"""
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    module = models.CharField(max_length=100)
    session = models.ForeignKey(GestureSession, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
    
    def __str__(self):
        return f"{self.level} - {self.module} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
