# 🤟 Hand Gesture Communication App

A revolutionary Django web application that bridges the communication gap between deaf and hearing individuals through real-time hand gesture recognition, text-to-sign language conversion, and voice-to-sign language translation.

## 🚀 Live Demo
[Visit the Website](https://mego354.github.io/Hand-Gesture-Project/)

## 🌟 Overview

This application serves as a comprehensive communication platform that enables seamless interaction between deaf and hearing individuals. It combines cutting-edge machine learning, computer vision, and web technologies to provide real-time gesture recognition, text translation, and voice processing capabilities.

## ✨ Key Features

### 🎯 **Core Functionality**
- **Real-time Hand Gesture Recognition**: Live camera feed processing with ML-powered gesture detection
- **Text-to-Sign Language**: Convert written text into sign language videos
- **Voice-to-Sign Language**: Transform voice recordings into sign language videos
- **Bidirectional Communication**: Full communication flow between deaf and hearing users
- **Multi-language Support**: Arabic and English language support

### 🚀 **Advanced Features**
- **Modern WebSocket Communication**: Real-time updates and instant feedback
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Video Processing**: Advanced video concatenation and optimization
- **Speech Recognition**: High-accuracy voice-to-text conversion
- **Session Management**: Track and manage communication sessions
- **Error Handling**: Comprehensive error management and user feedback

## 🛠 Technology Stack

### **Backend**
- **Django 4.2+**: Modern web framework with class-based views
- **Django Channels**: WebSocket support for real-time communication
- **TensorFlow/Keras**: Machine learning model for gesture recognition
- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Hand detection and tracking
- **SpeechRecognition**: Voice-to-text conversion
- **PyDub**: Audio processing and format conversion

### **Frontend**
- **Modern JavaScript**: ES6+ with async/await patterns
- **TensorFlow.js**: Browser-based machine learning
- **WebRTC API**: Camera and microphone access
- **Bootstrap 5**: Responsive UI framework
- **CSS3**: Modern styling with animations and transitions

### **Infrastructure**
- **SQLite**: Lightweight database (easily upgradeable to PostgreSQL)
- **Redis**: Channel layer for WebSocket communication
- **FFmpeg**: Video processing and format conversion
- **WebSockets**: Real-time bidirectional communication

## 📋 Prerequisites

- **Python 3.8+**
- **Redis Server** (for WebSocket functionality)
- **Webcam Access** (for gesture recognition)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **FFmpeg** (for video processing)

## 🔧 Installation & Setup

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/Hand-Gesture-Project.git
cd Hand-Gesture-Project
```

### 2. **Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Install Redis**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 5. **Install FFmpeg**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

### 6. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. **Run the Application**
```bash
python manage.py runserver
```

### 8. **Access the Application**
Open your browser and navigate to: `http://localhost:8000`

## 🎮 Usage Guide

### **For Deaf Users**
1. **Gesture Recognition**: Use the live stream feature to perform hand gestures
2. **View Responses**: Receive text and voice messages from hearing users
3. **Session Management**: Track your communication history

### **For Hearing Users**
1. **Text Input**: Type messages that get converted to sign language videos
2. **Voice Recording**: Record voice messages for automatic conversion
3. **View Gestures**: Watch sign language videos from deaf users

### **Communication Flow**
```
Deaf User (Gestures) → Text/Voice → Hearing User
Hearing User (Text/Voice) → Sign Language Video → Deaf User
```

## 🔌 API Endpoints

### **Core Endpoints**
- `POST /upload_text/` - Convert text to sign language
- `POST /upload_voice/` - Convert voice to sign language
- `POST /upload/` - Upload gesture videos for recognition
- `GET /stream/` - Live gesture recognition interface
- `GET /response/` - Communication interface

### **API Usage Examples**

#### **Text to Sign Language**
```bash
curl -X POST http://localhost:8000/upload_text/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Hello World"
```

#### **Voice to Sign Language**
```bash
curl -X POST http://localhost:8000/upload_voice/ \
  -F "voiceNote=@recording.webm"
```

#### **Response Format**
    ```json
    {
  "success": true,
  "text": "Hello World",
  "videosrc": "/media/concatenated_video.mp4",
  "message": "Text converted to sign language successfully"
}
```

## 🏗 Project Structure

```
Hand-Gesture-Project/
├── myprojectv3/                 # Django project configuration
│   ├── settings.py             # Main settings
│   ├── asgi.py                 # ASGI configuration
│   └── urls.py                 # URL routing
├── video_app/                  # Main application
│   ├── models.py               # Database models
│   ├── views.py                # Class-based views
│   ├── forms.py                # Django forms
│   ├── consumers.py            # WebSocket consumers
│   ├── routing.py              # WebSocket routing
│   ├── video_processing.py     # Video processing logic
│   ├── middleware.py           # Custom middleware
│   ├── utils.py                # Utility functions
│   ├── models/                 # ML models
│   │   └── model.h5           # Gesture recognition model
│   └── templates/              # HTML templates
│       ├── index.html         # Homepage
│       ├── text_to_sign.html  # Text conversion interface
│       ├── voice_to_sign.html # Voice conversion interface
│       ├── response.html      # Communication interface
│       └── stream.html        # Live gesture recognition
├── media/                      # Media files and videos
├── logs/                       # Application logs
└── requirements.txt            # Python dependencies
```

## 🎯 Key Components

### **Models**
- **HandGesture**: Stores recognized gestures and metadata
- **TextToSign**: Manages text-to-sign language conversions
- **VoiceToSign**: Handles voice-to-sign language processing
- **GestureSession**: Tracks user sessions and interactions

### **Views**
- **TextToSignView**: Handles text input and conversion
- **VoiceToSignView**: Manages voice recording and processing
- **StreamView**: Real-time gesture recognition interface
- **ResponseView**: Communication interface for both user types

### **WebSocket Consumers**
- **GestureConsumer**: Real-time gesture processing
- **CommunicationConsumer**: Bidirectional communication handling

## 🛡 Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **Input Validation**: Comprehensive form and data validation
- **File Type Validation**: Secure file upload handling
- **XSS Protection**: Cross-site scripting prevention
- **Rate Limiting**: API abuse prevention
- **Request Logging**: Comprehensive audit trail

## 🚀 Deployment

### **Production Setup**

1. **Environment Configuration**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secret-key'
```

2. **Database Configuration**
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

3. **Redis Configuration**
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

4. **Production Server**
```bash
pip install gunicorn uvicorn
gunicorn myprojectv3.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Redis Connection Error**
   ```bash
   redis-cli ping  # Should return PONG
   sudo systemctl start redis-server
   ```

2. **Camera Access Denied**
   - Grant camera permissions in browser
   - Use HTTPS for production (required for camera access)

3. **Model Loading Error**
   - Ensure `model.h5` exists in `video_app/models/`
   - Check file permissions and TensorFlow installation

4. **WebSocket Connection Failed**
   - Verify Redis is running
   - Check firewall settings
   - Ensure WebSocket support in browser

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Team** for the excellent web framework
- **TensorFlow Team** for machine learning capabilities
- **MediaPipe Team** for hand detection technology
- **OpenCV Community** for computer vision tools
- **SpeechRecognition Library** for voice processing
- **Bootstrap Team** for responsive UI components

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/Hand-Gesture-Project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Hand-Gesture-Project/discussions)
- **Email**: your.email@example.com

## 🌟 Future Enhancements

- [ ] Multi-language sign language support
- [ ] Mobile app development (React Native/Flutter)
- [ ] Advanced gesture recognition with more gestures
- [ ] Integration with external communication platforms
- [ ] Offline mode support
- [ ] Advanced analytics and usage tracking

---

**Made with ❤️ for the deaf and hard-of-hearing community**

*This application represents a significant step forward in accessible communication technology, bridging the gap between deaf and hearing individuals through innovative use of machine learning and web technologies.*
