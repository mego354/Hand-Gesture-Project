from django.contrib import admin
from .models import GestureSession, HandGesture, TextToSign, VoiceToSign, SystemLog


@admin.register(GestureSession)
class GestureSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['session_name', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(HandGesture)
class HandGestureAdmin(admin.ModelAdmin):
    list_display = ['gesture_type', 'confidence_score', 'session', 'created_at']
    list_filter = ['gesture_type', 'created_at', 'session']
    search_fields = ['gesture_type', 'session__session_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']


@admin.register(TextToSign)
class TextToSignAdmin(admin.ModelAdmin):
    list_display = ['input_text', 'processing_status', 'session', 'created_at']
    list_filter = ['processing_status', 'created_at', 'session']
    search_fields = ['input_text', 'session__session_name']
    readonly_fields = ['id', 'created_at', 'completed_at']
    ordering = ['-created_at']


@admin.register(VoiceToSign)
class VoiceToSignAdmin(admin.ModelAdmin):
    list_display = ['transcribed_text', 'processing_status', 'session', 'created_at']
    list_filter = ['processing_status', 'created_at', 'session']
    search_fields = ['transcribed_text', 'session__session_name']
    readonly_fields = ['id', 'created_at', 'completed_at']
    ordering = ['-created_at']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'module', 'message', 'session', 'created_at']
    list_filter = ['level', 'module', 'created_at']
    search_fields = ['message', 'module']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # Prevent manual log creation
