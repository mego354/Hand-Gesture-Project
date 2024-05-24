USAGE FROM A to Z

1. Instal PYTHON 3.8.0
choose the propriate version for your os from the officail site: https://www.python.org/downloads/release/python-380/
REAM the instruction there.
2. open vscode and run this command "python --version" if it's  3.8.0, continue if not restart vscode
3. run "python -m pip install --upgrade pip"
4. restart vscode
5. run "pip install django"
6. run "git clone https://github.com/mego354/hand_gestures.git"
7. cd hand_gestures (or myprojectv3 as the downloaded folder's name)
8. run "pip install -r requirements.txt"
9.restart vscode
10.open CMD run "ifconfig" and look for ipv4 and save it's address for now 
11. cd hand_gestures (or myprojectv3 as the downloaded folder's name)
12. get the file myprojectv3/settings.py line 28 paste the address
13. get your network IP paste it for line 29 "NETWORK_IP"
11. run "python manage.py runserver ipv4_Adress:8000 ", 

if your laptop’s IP address is 192.168.1.100, use the following command:
bash
run "python manage.py runserver 192.168.1.100:8000"

NOW THE SITE SHOULD BE WORKING ON !!!!!!!!!

to unable system firewall on the local host device:


Windows:
Open Command Prompt by pressing Win + R, typing cmd, and hitting Enter.
In the Command Prompt, type ipconfig and press Enter.
Look for the "IPv4 Address" under the active network connection. It will look something like 192.168.1.xxx.



1. to Open Windows Defender Firewall and Advanced Settings

2. Press Win + R to open the Run dialog.
3. Type wf.msc and press Enter. This opens the Windows Defender Firewall with Advanced Security.

Create a New Inbound Rule

4. In the left pane, click on "Inbound Rules."
5. In the right pane, click on "New Rule..." This opens the New Inbound Rule Wizard.
6. Configure the Rule
7. Rule Type: Select "Port" and click Next.

Protocol and Ports:

8. Select "TCP."
9. Select "all local ports"
Click Next.

Action:

10.select "Allow the connection."
Click Next.

Profile:
Click Next.
Name:
Give the rule a name, such as "Django Development Server."
Optionally, provide a description.
Click Finish.

now on the other device to access the page
on a new tab write this url "ipv4_Adress:8000", 

if your main laptop’s IP address is 192.168.1.100, use the following command:

url =  192.168.1.100:8000

app's routes:
main route is the stream:  192.168.1.100:8000 + ""
to get the response (the other person window): 192.168.1.100:8000 + get_latest_video/
<!--                                                  -->

API: 192.168.1.100:8000 + upload/
the uploaded video name: "video" 

the response will be json data as:

{"statue":True, "text":text, "videosrc":last_video_path}
or:
{"statue":False}

first check statue if true you are free to use the last_video_path to access the VIDEO

DONE!