from django.urls import reverse
import pytest
from reviews.models import Review

# Create your tests here.
pytestmark = pytest.mark.django_db

def test_create_review_and_redirect(client):
    url = reverse("reviews:review_list")
    response = client.post(
        url, {"author": "  Амалия  ", "text": "  Отличный сайт!  "}
    )

    assert response.status_code == 302
    assert response.url == url

    review = Review.objects.get()
    assert review.author == "Амалия"
    assert review.text == "Отличный сайт!"

    # Проверяем, что отзыв отображается на странице
    page = client.get(url).content.decode()
    assert "Амалия" in page
    assert "Отличный сайт!" in page


# 2. Тест отклонения пустых строк и строк из пробелов
@pytest.mark.parametrize(
    "author, text",
    [
        ("", "Нормальный текст"),
        ("   ", "Нормальный текст"),
        ("Амалия", ""),
        ("Амалия", "   "),
    ],
)
def test_reject_invalid_review_input(client, author, text):
    url = reverse("reviews:review_list")
    response = client.post(url, {"author": author, "text": text})

    assert response.status_code == 400
    assert not Review.objects.exists()