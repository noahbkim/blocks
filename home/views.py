from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import datetime
import json

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
    times = map(lambda x: (x // 6, x % 6), range(0, 24*6))
    blocks = models.get_blocks(request.user, today)
    return render(request, "home/home.html", {
        "today": today.strftime("%B %d, %Y"),
        "times": times,
        "blocks": blocks})


@login_required(login_url="/login/")
@csrf_exempt
def api(request):
    """The request API."""

    data = json.loads(request.body.decode())

    return HttpResponse("{}")


"""
set-activity
  activity
  blocks
"""
