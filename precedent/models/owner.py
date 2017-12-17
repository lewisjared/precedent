from django.db import models

from djchoices import ChoiceItem, DjangoChoices


class Owner(models.Model):
    class OwnerType(DjangoChoices):
        user = ChoiceItem('U')
        organisation = ChoiceItem('O')

    remote_id = models.IntegerField()
    name = models.TextField()
    type = models.CharField(max_length=1, choices=OwnerType.choices)
    url = models.URLField()
    avatar_url = models.URLField(null=True)
