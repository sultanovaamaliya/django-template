from django.db import models

# Create your models here.
class Review(models.Model):
    author = models.CharField("Автор", max_length=120)
    text = models.TextField("Отзыв", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.author}: {self.text[:30]}"
