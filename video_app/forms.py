# video_app/forms.py
from django import forms

class VideoUploadForm(forms.Form):
    video = forms.FileField()

class TextInputForm(forms.Form):
    text_input = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter text here', 'id': 'text_input'}),
        required = True
    )
