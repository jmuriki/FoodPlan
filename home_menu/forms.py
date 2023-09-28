from django import forms
from .models import Customer


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['image']
