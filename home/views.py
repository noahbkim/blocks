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
def view_home(request, date=None):
    """Blocks index page."""

    if date == "":
        date = None

    today = datetime.date.today()
    day = today if date is None else datetime.datetime.strptime(date, "%Y%m%d").date()
    tomorrow = None if day >= today else datetime.date(day.year, day.month, day.day + 1)
    yesterday = datetime.date(day.year, day.month, day.day - 1)

    times = map(lambda x: (x // 6, x % 6), range(0, 24*6))

    blocks = models.get_blocks(request.user, day)
    return render(request, "home/home.html", {
        "today": day.strftime("%B %d, %Y"),
        "times": times,
        "blocks": blocks,
        "tomorrow": None if not tomorrow else tomorrow.strftime("%Y%m%d"),
        "yesterday": yesterday.strftime("%Y%m%d"),
    })


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
            if "date" in data:
                date = datetime.datetime.strptime(data["date"], "%Y%m%d").date()
            else:
                date = datetime.date.today()
            dt = datetime.datetime(date.year, date.month, date.day, *map(int, time.split(":")))
            block = models.Block.objects.create(user=request.user, datetime=dt, activity=activity)
            block.save()
        result = {"result": "success"}
    if data["command"] == "get-blocks":
        date = {}
        if "date" in data:
            date["date"] = datetime.datetime.strptime(data["date"], "%Y%m%d").date()
        blocks = models.get_blocks(request.user, **date)
        result.update({"blocks": list(map(lambda x: x.to_json(), blocks))})
    return HttpResponse(json.dumps(result))


"""
set-activity
  activity
  blocks
"""
