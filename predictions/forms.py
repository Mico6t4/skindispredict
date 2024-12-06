from django import forms
from .models import PredictionResult

class PredictionResultForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    predicted_class = forms.CharField(required=False)
    confidence = forms.FloatField(required=False)

    class Meta:
        model = PredictionResult
        fields = ['image', 'predicted_class', 'confidence']
