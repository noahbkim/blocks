from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """A profile model that contains blocks data."""

    user = models.ForeignKey(User)


class Category(models.Model):
    """A category of activity."""

    name = models.CharField(max_length=30)


class Tag(models.Model):
    """A custom tag that describes an activity."""

    name = models.CharField(max_length=30)
    creator = models.ForeignKey(Profile, related_name="tags")


class Activity(models.Model):
    """An activity container."""

    name = models.CharField(max_length=60)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag)
    color = models.CharField(max_length=7)
    creator = models.ForeignKey(Profile, related_name="activites")

