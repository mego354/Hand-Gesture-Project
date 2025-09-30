# Hand Gesture Recognition System - Upgraded with Django Channels

This is an upgraded version of the hand gesture recognition system using Django Channels for real-time communication and following Django best practices.

## 🚀 New Features

- **Real-time WebSocket Communication**: Uses Django Channels for instant feedback
- **Modern Class-based Views**: Following Django best practices
- **Comprehensive Models**: Proper database structure with relationships
- **Advanced Security**: Custom middleware for security and logging
- **Session Management**: Organize and track gesture recognition sessions
- **Search and Filtering**: Advanced search capabilities for gestures
- **Responsive UI**: Modern, mobile-friendly interface
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in rate limiting for API endpoints

## 🛠 Technology Stack

- **Backend**: Django 4.2.13 with Django Channels 4.0.0
- **Real-time**: WebSockets with Redis as channel layer
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Frontend**: Modern JavaScript with TensorFlow.js
- **Computer Vision**: OpenCV, MediaPipe, TensorFlow
- **Audio Processing**: SpeechRecognition, PyDub

## 📋 Prerequisites

- Python 3.8+
- Redis server
- Webcam access
- Modern web browser with WebSocket support

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Hand-Gesture-Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Redis**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis-server
   
   # On macOS
   brew install redis
   brew services start redis
   
   # On Windows
   # Download Redis from https://github.com/microsoftarchive/redis/releases
   ```

5. **Set up the system**
   ```bash
   python manage.py setup_system --create-superuser
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - Use the admin interface at `http://localhost:8000/admin/`

## 🏗 Project Structure

```
Hand-Gesture-Project/
├── myprojectv3/                 # Django project settings
│   ├── settings.py             # Main settings with Channels config
│   ├── asgi.py                 # ASGI configuration for WebSockets
│   └── urls.py                 # Main URL configuration
├── video_app/                  # Main application
│   ├── models.py               # Database models
│   ├── views.py                # Class-based views
│   ├── forms.py                # Django forms with validation
│   ├── consumers.py            # WebSocket consumers
│   ├── routing.py              # WebSocket routing
│   ├── video_processing.py     # Async video processing
│   ├── middleware.py           # Custom middleware
│   ├── utils.py                # Utility functions
│   ├── admin.py                # Admin configuration
│   └── templates/              # HTML templates
│       ├── index_modern.html   # Modern homepage
│       └── stream_modern.html  # Real-time gesture recognition
├── media/                      # Media files
├── logs/                       # Application logs
└── requirements.txt            # Python dependencies
```

## 🎯 Key Components

### Models
- **GestureSession**: Manages user sessions
- **HandGesture**: Stores recognized gestures
- **TextToSign**: Text-to-sign language conversions
- **VoiceToSign**: Voice-to-sign language conversions
- **SystemLog**: Application logging

### WebSocket Consumers
- **GestureConsumer**: Handles real-time gesture processing
- **GestureStreamConsumer**: Manages gesture streaming

### Views
- **IndexView**: Modern homepage
- **SessionListView**: List user sessions
- **GestureStreamView**: Real-time gesture recognition
- **API Views**: RESTful endpoints for WebSocket integration

## 🔌 WebSocket Endpoints

- `ws://localhost:8000/ws/gesture-session/{session_id}/` - Individual session
- `ws://localhost:8000/ws/gesture-stream/` - Global gesture stream

## 🛡 Security Features

- **CSRF Protection**: Built-in CSRF protection
- **Rate Limiting**: Prevents abuse with rate limiting
- **Input Validation**: Comprehensive form validation
- **File Type Validation**: Secure file upload handling
- **XSS Protection**: Cross-site scripting protection
- **Request Logging**: Comprehensive request/response logging

## 📊 Monitoring and Logging

- **System Logs**: Database-stored system events
- **Request Tracking**: Unique request IDs for tracing
- **Performance Monitoring**: Response time tracking
- **Error Handling**: Comprehensive error logging

## 🚀 Deployment

### Production Settings

1. **Update settings.py**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-secret-key'
   ```

2. **Use PostgreSQL**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Configure Redis**
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('your-redis-host', 6379)],
           },
       },
   }
   ```

4. **Use Gunicorn with Uvicorn**
   ```bash
   pip install gunicorn uvicorn
   gunicorn myprojectv3.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

### Redis Configuration
Ensure Redis is running and accessible:
```bash
redis-cli ping
# Should return PONG
```

## 📱 Usage

1. **Create a Session**: Start by creating a new gesture recognition session
2. **Real-time Recognition**: Use the stream interface for live gesture recognition
3. **Text to Sign**: Convert text to sign language videos
4. **Voice to Sign**: Convert voice recordings to sign language
5. **Session Management**: View and manage your recognition sessions

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   redis-cli ping
   
   # Start Redis if not running
   sudo systemctl start redis-server
   ```

2. **WebSocket Connection Failed**
   - Ensure Redis is running
   - Check firewall settings
   - Verify WebSocket support in browser

3. **Model Loading Error**
   - Ensure model.h5 file exists in video_app/models/
   - Check file permissions
   - Verify TensorFlow installation

4. **Camera Access Denied**
   - Grant camera permissions in browser
   - Use HTTPS for production (required for camera access)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django Channels team for WebSocket support
- TensorFlow.js team for browser-based ML
- MediaPipe team for hand detection
- OpenCV community for computer vision tools

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the Django Channels documentation

---

**Note**: This is an upgraded version with modern Django practices, real-time capabilities, and enhanced security. The original functionality is preserved while adding significant improvements in architecture, user experience, and maintainability.
