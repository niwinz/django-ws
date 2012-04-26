from django.db import models

class Visits(models.Model):
    ref = models.CharField(max_length=200)
