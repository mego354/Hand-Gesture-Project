# video_app/forms.py
from django import forms

class VideoUploadForm(forms.Form):
    video = forms.FileField()
