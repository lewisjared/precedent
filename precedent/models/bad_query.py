from django.db import models


class BadQuery(models.Model):
    date = models.DateTimeField(auto_now=True)
    query = models.TextField()