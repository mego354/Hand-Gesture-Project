"""
WebSocket consumers for real-time hand gesture processing
"""
import json
import asyncio
import logging
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import GestureSession, HandGesture, SystemLog
# Lazy imports to avoid loading heavy libraries during startup
# from .video_processing import process_gesture_video_async

logger = logging.getLogger(__name__)


class GestureConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for individual gesture sessions"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'gesture_session_{self.session_id}'
        
        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection
        await self.log_system_event('INFO', f'WebSocket connected to session {self.session_id}')
        
        # Send initial session data
        session_data = await self.get_session_data()
        await self.send(text_data=json.dumps({
            'type': 'session_data',
            'data': session_data
        }))
    
    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )
        
        await self.log_system_event('INFO', f'WebSocket disconnected from session {self.session_id}')
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'gesture_video':
                await self.handle_gesture_video(data)
            elif message_type == 'text_to_sign':
                await self.handle_text_to_sign(data)
            elif message_type == 'voice_to_sign':
                await self.handle_voice_to_sign(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_gesture_video(self, data):
        """Handle incoming gesture video data"""
        try:
            video_data = data.get('video_data')
            print(f"🔍 [DEBUG] WebSocket received video data: {len(video_data) if video_data else 0} bytes")
            
            if not video_data:
                print(f"❌ [DEBUG] No video data provided to WebSocket")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'No video data provided'
                }))
                return
            
            # Send processing status
            await self.send(text_data=json.dumps({
                'type': 'processing_status',
                'status': 'processing',
                'message': 'Processing gesture video...'
            }))
            
            print(f"🔍 [DEBUG] Starting WebSocket video processing...")
            
            # Import and process the gesture video asynchronously
            from .video_processing import process_gesture_video_async
            result = await process_gesture_video_async(video_data, self.session_id)
            
            print(f"🔍 [DEBUG] WebSocket processing result: {result}")
            
            if result['success']:
                print(f"✅ [DEBUG] WebSocket processing successful: {result['gesture_type']}")
                # Save gesture to database
                gesture = await self.save_gesture(result)
                
                # Send result to session group
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'gesture_result',
                        'gesture_type': result['gesture_type'],
                        'confidence': result['confidence'],
                        'gesture_id': str(gesture.id),
                        'video_url': result.get('video_url')
                    }
                )
            else:
                print(f"❌ [DEBUG] WebSocket processing failed: {result.get('error')}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Failed to process gesture')
                }))
                
        except Exception as e:
            print(f"❌ [DEBUG] WebSocket exception: {str(e)}")
            logger.error(f"Error handling gesture video: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process gesture video'
            }))
    
    async def handle_text_to_sign(self, data):
        """Handle text-to-sign conversion requests"""
        try:
            text = data.get('text', '').strip()
            if not text:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'No text provided'
                }))
                return
            
            # Send processing status
            await self.send(text_data=json.dumps({
                'type': 'processing_status',
                'status': 'processing',
                'message': 'Converting text to sign language...'
            }))
            
            # Import and process text to sign
            from .video_processing import process_text_to_sign_async
            result = await process_text_to_sign_async(text, self.session_id)
            
            if result['success']:
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'text_to_sign_result',
                        'input_text': text,
                        'video_url': result.get('video_url'),
                        'conversion_id': result.get('conversion_id')
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Failed to convert text to sign')
                }))
                
        except Exception as e:
            logger.error(f"Error handling text to sign: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process text to sign conversion'
            }))
    
    async def handle_voice_to_sign(self, data):
        """Handle voice-to-sign conversion requests"""
        try:
            audio_data = data.get('audio_data')
            if not audio_data:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'No audio data provided'
                }))
                return
            
            # Send processing status
            await self.send(text_data=json.dumps({
                'type': 'processing_status',
                'status': 'processing',
                'message': 'Converting voice to sign language...'
            }))
            
            # Import and process voice to sign
            from .video_processing import process_voice_to_sign_async
            result = await process_voice_to_sign_async(audio_data, self.session_id)
            
            if result['success']:
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'voice_to_sign_result',
                        'transcribed_text': result.get('transcribed_text'),
                        'video_url': result.get('video_url'),
                        'conversion_id': result.get('conversion_id')
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Failed to convert voice to sign')
                }))
                
        except Exception as e:
            logger.error(f"Error handling voice to sign: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process voice to sign conversion'
            }))
    
    # WebSocket event handlers
    async def gesture_result(self, event):
        """Send gesture recognition result to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'gesture_result',
            'gesture_type': event['gesture_type'],
            'confidence': event['confidence'],
            'gesture_id': event['gesture_id'],
            'video_url': event.get('video_url')
        }))
    
    async def text_to_sign_result(self, event):
        """Send text-to-sign result to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'text_to_sign_result',
            'input_text': event['input_text'],
            'video_url': event['video_url'],
            'conversion_id': event['conversion_id']
        }))
    
    async def voice_to_sign_result(self, event):
        """Send voice-to-sign result to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'voice_to_sign_result',
            'transcribed_text': event['transcribed_text'],
            'video_url': event['video_url'],
            'conversion_id': event['conversion_id']
        }))
    
    # Database operations
    @database_sync_to_async
    def get_session_data(self):
        """Get session data from database"""
        try:
            session = GestureSession.objects.get(id=self.session_id)
            gestures = HandGesture.objects.filter(session=session).order_by('-created_at')[:10]
            
            return {
                'session_id': str(session.id),
                'session_name': session.session_name,
                'created_at': session.created_at.isoformat(),
                'recent_gestures': [
                    {
                        'id': str(gesture.id),
                        'gesture_type': gesture.gesture_type,
                        'confidence': gesture.confidence_score,
                        'created_at': gesture.created_at.isoformat()
                    }
                    for gesture in gestures
                ]
            }
        except GestureSession.DoesNotExist:
            return {'error': 'Session not found'}
    
    @database_sync_to_async
    def save_gesture(self, result):
        """Save gesture result to database"""
        try:
            session = GestureSession.objects.get(id=self.session_id)
            gesture = HandGesture.objects.create(
                session=session,
                gesture_type=result['gesture_type'],
                confidence_score=result['confidence']
            )
            return gesture
        except Exception as e:
            logger.error(f"Error saving gesture: {str(e)}")
            raise
    
    @database_sync_to_async
    def log_system_event(self, level, message):
        """Log system event to database"""
        try:
            session = GestureSession.objects.get(id=self.session_id)
            SystemLog.objects.create(
                level=level,
                message=message,
                module='WebSocket Consumer',
                session=session
            )
        except Exception as e:
            logger.error(f"Error logging system event: {str(e)}")
    


class GestureStreamConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time gesture streaming"""
    
    async def connect(self):
        self.stream_group_name = 'gesture_stream'
        
        # Join stream group
        await self.channel_layer.group_add(
            self.stream_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info("Gesture stream WebSocket connected")
    
    async def disconnect(self, close_code):
        # Leave stream group
        await self.channel_layer.group_discard(
            self.stream_group_name,
            self.channel_name
        )
        logger.info("Gesture stream WebSocket disconnected")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'stream_data':
                # Broadcast stream data to all connected clients
                await self.channel_layer.group_send(
                    self.stream_group_name,
                    {
                        'type': 'stream_update',
                        'data': data.get('data')
                    }
                )
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in stream receive: {str(e)}")
    
    async def stream_update(self, event):
        """Send stream update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'stream_update',
            'data': event['data']
        }))
