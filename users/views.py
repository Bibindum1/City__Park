from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Регистрация прошла успешно!"
            )

            return redirect("index")

        messages.error(
            request,
            "Исправьте ошибки в форме."
        )

    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form
        }
    )


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                f"Добро пожаловать, {user.get_username()}!"
            )

            return redirect("index")

        messages.error(
            request,
            "Неверный логин или пароль."
        )

    else:
        form = LoginForm()

    return render(
        request,
        "registration/login.html",
        {
            "form": form
        }
    )