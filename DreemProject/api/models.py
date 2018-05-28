"""
Dreem project's models.
"""
from django.db import models

# TODO: set limits/max_length, etc to the fields.

class Device(models.Model):
    """A device. Which is worn by clients."""
    name = models.SlugField(unique=True)
    dreempy_version = models.CharField(max_length=12) # e.g.: XXX.XXX.XXX
    date_registered = models.DateTimeField(auto_now_add=True)

    # TODO add remaining fields.

class Record(models.Model):
    """A device's record made during the night."""
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField()

    sleep_start_time = models.DateTimeField()
    sleep_stop_time = models.DateTimeField()
    sleep_score = models.DecimalField(max_digits=17, decimal_places=16) # to be confirmed

    number_of_stimulations = models.PositiveSmallIntegerField()
    number_of_wake = models.PositiveSmallIntegerField()
    hypnogram = models.TextField() # TODO: use something smarter, that can be queried.

    # I use the provided Django user table.
    user = models.ForeignKey("auth.User", models.CASCADE, to_field="username")
    device = models.ForeignKey(Device, models.CASCADE)

    # TODO add remaining fields.
