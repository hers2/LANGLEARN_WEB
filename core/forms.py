from django import forms
from .models import VocabularyQuestion


class VocabularyQuestionForm(forms.ModelForm):
    class Meta:
        model = VocabularyQuestion
        fields = [
            'question', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'category', 'difficulty', 'is_active'
        ]
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tulis pertanyaan vocabulary di sini...'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Pilihan A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Pilihan B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Pilihan C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Pilihan D'}),
        }
