# Hand Gesture Recognition Project

## Overview
This project is a Django web application designed to facilitate real-time communication between a deaf person and a hearing person. The application uses machine learning to translate hand gestures into text and videos. It includes APIs for integrating with Flutter applications.

## Technologies Used
- Django
- JavaScript
- Bootstrap
- TensorFlow
- Keras
- OpenCV
- WebRTC API
- Google Charts

### Features
- **Deaf Person View**: Streams hand gestures, translates them into text and video, and sends them to a hearing person.
- **Hearing Person View**: Receives video and text messages from the deaf person, and can reply via text or voice note, which are then translated into hand gesture videos for the deaf person.
- **Real-Time Communication**: Ensures smooth and instant interaction between the two parties.
- **APIs**: Provides endpoints for gesture recognition and translation services.

## Usage Guide

### Installation

1. **Install Python 3.8.0**:
   - Download from the official site: [Python 3.8.0 Downloads](https://www.python.org/downloads/release/python-380/)
   - Follow the installation instructions.

2. **Verify Python Installation in VS Code**:
   - Open VS Code and run `python --version`.
   - Ensure it shows version `3.8.0`.

3. **Upgrade Pip**:
   - Run `python -m pip install --upgrade pip`.

4. **Install Django**:
   - Run `pip install django`.

5. **Clone the Project Repository**:
   - Run `git clone https://github.com/mego354/Hand-Gesture.git`.

6. **Navigate to Project Directory**:
   - Run `cd Hand-Gesture`.

7. **Install Requirements**:
   - Run `pip install -r requirements.txt`.

8. **Download and Install ffmpeg**:
   - Follow the installation instructions provided in this [ffmpeg guide](https://youtu.be/DMEP82yrs5g?si=MQEmjjjLUsmxbItw).

### Configuration

1. **Set Up IP Address**:
   - Obtain your IPv4 address by running `ipconfig` in the command prompt (needed for API usage).

### Running the Development Server

1. **Start the Django Server**:
   - Run:
     ```sh
     python manage.py runsslserver ipv4_address:8000
     ```
   - Replace `ipv4_address` with your actual IPv4 address.

### Firewall Configuration (Windows)

1. **Open Windows Defender Firewall and Advanced Settings**:
   - Press `Win + R`, type `wf.msc`, and press Enter.

2. **Create a New Inbound Rule**:
   - In the left pane, click on **Inbound Rules**.
   - Click **New Rule...**.

3. **Configure the Rule**:
   - Rule Type: Select **Port**.
   - Protocol and Ports: Select **TCP** and **Specific local ports**, enter `8000`.
   - Action: Select **Allow the connection**.
   - Profile: Leave all options checked.
   - Name: Name it "Django Development Server".
   - Finish the wizard.

### Accessing the Application

- On any device, open a browser and go to:
  ```
  https://ipv4_address:8000/
  ```
  Replace `ipv4_address` with your actual IPv4 address.

### Application Routes

- **Main Route**: `ipv4_address:8000`
  - Choose either Deaf or Hearing Person view.
- **Deaf Route (Live Stream)**: `ipv4_address:8000/stream/`
- **Response Route (Other Person's Window)**: `ipv4_address:8000/response/`
- **API Endpoints**:
  - **Upload Video**: `ipv4_address:8000/upload/` (accepts raw video for hand gesture, at least 4 seconds)
    ```json
    {
      "video": "video.mp4"
    }
    ```
  - **Upload Text**: `ipv4_address:8000/upload_text/` (accepts text)
    ```json
    {
      "text_input": "hello my friend"
    }
    ```
  - **Upload Voice Note**: `ipv4_address:8000/upload_voice/` (accepts voice note)
    ```json
    {
      "voiceNote": "voicenote.m4a"
    }
    ```

### API Response

- **Upload a Video**: The parameter name for the video is "video".
- **Response JSON**:
  ```json
  {
    "status": true,
    "text": "translated_text",
    "videosrc": "path_to_video"
  }
  ```
  or
  ```json
  {
    "status": false
  }
  ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## Acknowledgements
This project was developed for a graduation project in the Faculty of Science. Special thanks to the team for their collaboration and support.

---

