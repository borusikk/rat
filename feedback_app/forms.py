from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Введите вашу корпоративную почту'}),
        help_text="Введите адрес корпоративной почты (например, имя@nure.ua)."
    )

    class Meta:
        model = Feedback
        fields = ['professionalism', 'clarity', 'attitude', 'comment', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@nure.ua'):
            raise forms.ValidationError("Вы должны использовать корпоративный адрес @nure.ua.")
        return email
