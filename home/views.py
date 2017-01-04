from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import datetime

from home import models


def view_index(request):
    """Blocks index page."""

    return render(request, "home/index.html")


def view_login(request):
    """User login page."""

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("/home/")
        return redirect("/login/?error=1")

    return render(request, "home/login.html")


def view_register(request):
    """Register for the blocks service."""

    if request.method == "POST":
        models.User.objects.create(
            username=request.POST["username"],
            email=request.POST["email"],
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            password=request.POST["password"])


def view_logout(request):
    """Logout the user."""

    logout(request)


@login_required(login_url="/login/")
def view_home(request):
    """Blocks index page."""

    today = datetime.date.today()
    blocks = models.get_blocks(request.user, today)

    return render(request, "home/home.html", {"blocks": blocks, "today": today.strftime("%B %d, %Y")})


def view_update(request):
    """Update the user's blocks for the day."""

    print(request.POST)
