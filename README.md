# Hand Gesture Recognition Project 

## Usage Guide

### Installation

1. **Install Python 3.8.0:**
   - Choose the appropriate version for your OS from the official site: [Python 3.8.0 Downloads](https://www.python.org/downloads/release/python-380/)
   - Follow the installation instructions provided.

2. **Verify Python Installation in VS Code:**
   - Open VS Code and run `python --version`.
   - Ensure the version displayed is `3.8.0`. If not, restart VS Code.

3. **Upgrade Pip:**
   - Run `python -m pip install --upgrade pip`.

4. **Install Django:**
   - Run `pip install django`.

5. **Clone the Project Repository:**
   - Run `git clone https://github.com/mego354/hands.git`.

6. **Navigate to Project Directory:**
   - Change directory to `hands` e.g. `cd hands`.

7. **Install Requirements:**
   - Run `pip install -r requirements.txt`.

### Configuration

1. **Set Up IP Address:**
   - Obtain your IPv4 address by running `ipconfig` in the command prompt "for API using".
### Running the Development Server

1. **Start the Django Server:**
   - In the command prompt, run:
     ```
     python manage.py runserver ipv4_address:8000
     ```
   - Replace `ipv4_address` with your IPv4 address.

   Example:
   ```
   python manage.py runsslserver 0.0.0.0:8000
   ```

### Firewall Configuration (Local Host Device)

#### For Windows:

1. **Open Windows Defender Firewall and Advanced Settings:**
   - Press `Win + R` to open the Run dialog.
   - Type `wf.msc` and press Enter.

2. **Create a New Inbound Rule:**
   - In the left pane, click on **Inbound Rules**.
   - Click **New Rule...** to open the wizard.

3. **Configure the Rule:**
   - Rule Type: Select **Port** and click Next.
   - Protocol and Ports: Select **TCP** and **Specific local ports**, enter `8000`.
   - Action: Select **Allow the connection**.
   - Profile: Leave all options checked and click Next.
   - Name: Provide a name like "Django Development Server".
   - Click **Finish** to complete.

### Accessing the Application

- On any device, open a web browser and enter the following URL:
  ```
  https://ipv4_address:8000/
  ```
  Replace `ipv4_address` with the IPv4 address of the main laptop.

  Example:
  ```
  https://192.168.1.5:8000/
  ```

### Application Routes

- Main Route (choose eaither Deaf or Normal): `ipv4_address:8000`
- Deaf Route (Live Stream): `ipv4_address:8000/stream/`
- To Get the Response (Other Person's Window): `ipv4_address:8000/response/`
- API Endpoint: `ipv4_address:8000/upload/`

### API Response

- Upload a video with the parameter name "video".
- Response JSON:
  ```json
  {
    "status": true,
    "text": "text",
    "videosrc": "last_video_path"
  }
  ```
  or
  ```json
  {
    "status": false
  }
  ```
  Check `status`; if `true`, use `videosrc` to access the video.

