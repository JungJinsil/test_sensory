from django import forms
from .models import SurveyResult

class SurveyForm(forms.ModelForm):
    class Meta:
        model = SurveyResult
        fields = ['taste_score', 'flavor_score']
