from django.forms import ModelForm, DateInput
from django import forms


class MeetingForm():
    def __init__(self, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)

