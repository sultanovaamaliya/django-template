from django.shortcuts import redirect, render
from .forms import ReviewForm
from .models import Review


def review_list(request):
    status = 200
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            # Перенаправляем (302 Redirect), чтобы F5 не отправлял форму повторно
            return redirect("reviews:review_list")
        status = 400
    else:
        form = ReviewForm()

    return render(
        request,
        "reviews/review_list.html",
        {"reviews": Review.objects.all(), "form": form},
        status=status,
    )