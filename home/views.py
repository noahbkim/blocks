from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import datetime
import json
import random

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
    return render(request, "home/home.html", {
        "today": today.strftime("%B %d, %Y"),
        "times": times})


@login_required(login_url="/login/")
@csrf_exempt
def api(request):
    """The request API."""

    data = json.loads(request.body.decode())
    result = {}
    if data["command"] == "set-blocks":
        name = data["activity"].lower()
        activity = models.Activity.objects.filter(name=name).first()
        if not activity:
            activity = models.Activity.objects.create(user=request.user, name=name)
            activity.color = "#%06x" % random.randint(0, 0xFFFFFF)
            activity.save()
        for time in data["blocks"]:
            today = datetime.date.today()
            dt = datetime.datetime(today.year, today.month, today.day, *map(int, time.split(":")))
            block = models.Block.objects.create(user=request.user, datetime=dt, activity=activity)
            block.save()
        result = {"result": "success"}
    if data["command"] == "get-blocks":
        blocks = models.get_blocks(request.user)
        result.update({"blocks": list(map(lambda x: x.to_json(), blocks))})
    return HttpResponse(json.dumps(result))


"""
set-activity
  activity
  blocks
"""
