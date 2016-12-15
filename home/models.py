from django.db import models
from django.contrib.auth.models import User

import datetime as dt


def tens(d: dt.datetime):
    """Round minutes of a datetime object to lower tens."""

    time = dt.datetime(d.hour, d.minute - d.minute % 10)
    return dt.datetime.combine(d.date(), time)


def to_tens(function):
    """Decorator for block API functions."""

    def wrapper(user, time, *args, **kwargs):
        return function(user, tens(time), *args, **kwargs)
    return wrapper


class Category(models.Model):
    """A category of activity."""

    name = models.CharField(max_length=30)


class Tag(models.Model):
    """A custom tag that describes an activity."""

    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name="tags")


class Activity(models.Model):
    """An activity container."""

    name = models.CharField(max_length=60)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag)
    color = models.CharField(max_length=7)
    user = models.ForeignKey(User, related_name="activites")


class Block(models.Model):
    """A container for time block information."""

    user = models.ForeignKey(User, related_name="blocks")
    datetime = models.DateTimeField()
    activity = models.ForeignKey(Activity)


def _create_block(user, datetime, activity):
    """Create a new time block for the given time."""

    datetime = tens(datetime)
    block = Block()
    block.user = user.user
    block.datetime = datetime
    block.activity = activity
    block.save()
    return block


@to_tens
def edit_block(user, datetime, activity):
    """Change the activity of a block at a time."""

    datetime = tens(datetime)
    block = Block.objects.filter(time=datetime).first()
    if block:
        block.activity = activity
        return block
    return Block._create_block(user, datetime, activity)


@to_tens
def get_block(user, datetime):
    """Get a block by its time."""

    datetime = tens(datetime)
    return Block.objects.filter(user=user, datetime=datetime).first()


@to_tens
def delete_block(user, datetime):
    """Delete a block entirely."""

    block = user.get_block(user, datetime)
    if block:
        block.delete()
