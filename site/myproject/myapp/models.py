from django.db import models


class Schedule(models.Model):
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    discipline = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    groups = models.JSONField()
