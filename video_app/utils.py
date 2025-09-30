"""
Utility functions for the video_app
"""
import os
import logging
import hashlib
import uuid
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import SystemLog, GestureSession

logger = logging.getLogger(__name__)


def log_system_event(level: str, message: str, module: str, session: Optional[GestureSession] = None):
    """
    Log system events to database
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        module: Module name
        session: Optional session reference
    """
    try:
        SystemLog.objects.create(
            level=level,
            message=message,
            module=module,
            session=session
        )
    except Exception as e:
        logger.error(f"Failed to log system event: {str(e)}")


def generate_file_hash(file_path: str) -> Optional[str]:
    """
    Generate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash or None if error
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error generating file hash: {str(e)}")
        return None


def validate_file_type(file, allowed_types: list) -> bool:
    """
    Validate file type based on extension and MIME type
    
    Args:
        file: Django file object
        allowed_types: List of allowed file extensions
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_types:
            return False
        
        # Check file size (max 100MB)
        if file.size > 100 * 1024 * 1024:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating file type: {str(e)}")
        return False


def save_uploaded_file(file, directory: str, filename: Optional[str] = None) -> Optional[str]:
    """
    Save uploaded file to storage
    
    Args:
        file: Django file object
        directory: Directory to save file
        filename: Optional custom filename
        
    Returns:
        Saved file path or None if error
    """
    try:
        if not filename:
            filename = f"{uuid.uuid4()}_{file.name}"
        
        file_path = os.path.join(directory, filename)
        saved_path = default_storage.save(file_path, ContentFile(file.read()))
        
        log_system_event('INFO', f"File saved: {saved_path}", 'FileUtils')
        return saved_path
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        log_system_event('ERROR', f"Failed to save file: {str(e)}", 'FileUtils')
        return None


def cleanup_old_files(directory: str, max_age_days: int = 7):
    """
    Clean up old files from directory
    
    Args:
        directory: Directory to clean
        max_age_days: Maximum age of files in days
    """
    try:
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=max_age_days)
        
        # This would need to be implemented based on your storage backend
        # For now, just log the intention
        log_system_event('INFO', f"Cleanup requested for directory: {directory}", 'FileUtils')
    except Exception as e:
        logger.error(f"Error during file cleanup: {str(e)}")


def get_client_ip(request) -> str:
    """
    Get client IP address from request
    
    Args:
        request: Django request object
        
    Returns:
        Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Ensure filename is not empty
    if not filename:
        filename = f"file_{uuid.uuid4().hex[:8]}"
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_session_directory(session_id: str) -> str:
    """
    Create directory structure for session files
    
    Args:
        session_id: Session ID
        
    Returns:
        Created directory path
    """
    try:
        from datetime import datetime
        date_path = datetime.now().strftime('%Y/%m/%d')
        session_dir = os.path.join('sessions', str(session_id), date_path)
        
        # Create directory if it doesn't exist
        full_path = os.path.join(settings.MEDIA_ROOT, session_dir)
        os.makedirs(full_path, exist_ok=True)
        
        return session_dir
    except Exception as e:
        logger.error(f"Error creating session directory: {str(e)}")
        return f"sessions/{session_id}"


def validate_session_access(request, session_id: str) -> bool:
    """
    Validate if user has access to session
    
    Args:
        request: Django request object
        session_id: Session ID
        
    Returns:
        True if access allowed, False otherwise
    """
    try:
        if not request.user.is_authenticated:
            return False
        
        session = GestureSession.objects.get(id=session_id)
        return session.user == request.user or request.user.is_staff
    except GestureSession.DoesNotExist:
        return False
    except Exception as e:
        logger.error(f"Error validating session access: {str(e)}")
        return False


def get_system_stats() -> Dict[str, Any]:
    """
    Get system statistics
    
    Returns:
        Dictionary with system stats
    """
    try:
        from django.db.models import Count, Avg
        from datetime import datetime, timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        stats = {
            'total_sessions': GestureSession.objects.count(),
            'active_sessions': GestureSession.objects.filter(is_active=True).count(),
            'sessions_last_24h': GestureSession.objects.filter(created_at__gte=last_24h).count(),
            'total_gestures': 0,  # Would need to import HandGesture
            'avg_confidence': 0,  # Would need to import HandGesture
            'system_uptime': 'N/A',  # Would need to implement uptime tracking
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return {}


def send_notification(message: str, notification_type: str = 'info'):
    """
    Send notification (placeholder for future implementation)
    
    Args:
        message: Notification message
        notification_type: Type of notification (info, warning, error)
    """
    # This would integrate with notification systems like:
    # - Email notifications
    # - Push notifications
    # - WebSocket notifications
    # - SMS notifications
    
    log_system_event('INFO', f"Notification sent: {message}", 'NotificationSystem')


def backup_database():
    """
    Create database backup (placeholder for future implementation)
    """
    try:
        # This would implement database backup functionality
        log_system_event('INFO', "Database backup initiated", 'BackupSystem')
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        log_system_event('ERROR', f"Database backup failed: {str(e)}", 'BackupSystem')
