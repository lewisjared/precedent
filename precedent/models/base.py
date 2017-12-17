from django.db import models
from django.utils import timezone


class AddedModifiedModel(models.Model):
    """
    Base Model which keeps track of added and modified datetimes

    This class inherits from Model as Django's Meta magic plays havoc with the fields descriptions. Inheriting from Model keeps the MRO linear.
    """
    added = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        super(AddedModifiedModel, self).save(*args, **kwargs)
