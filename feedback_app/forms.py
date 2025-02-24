from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['professionalism', 'clarity', 'attitude', 'comment']
        widgets = {
            'professionalism': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'clarity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'attitude': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    professionalism = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Професіоналізм (1-5)"
    )
    clarity = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Зрозумілість пояснення (1-5)"
    )
    attitude = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ставлення до студентів (1-5)"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label="Коментар"
    )
