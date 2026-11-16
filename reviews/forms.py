from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Поля и ограничения формы берём из модели Reviews."""

    class Meta:
        model = Review
        fields = ["author", "text"]

        def clean_author(self):
            author = self.cleaned_data.get("author", "").strip()
            if not author:
                raise forms.ValidationError("Имя автора не может быть пустым.")
            return author

        def clean_text(self):
            text = self.cleaned_data.get("text", "").strip()
            if not text:
                raise forms.ValidationError("Текст отзыва не может быть пустым.")
            return text
