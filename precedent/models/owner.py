from django.db import models

from djchoices import ChoiceItem, DjangoChoices


class Owner(models.Model):
    class OwnerType(DjangoChoices):
        user = ChoiceItem('U')
        organisation = ChoiceItem('O')

    class Source(DjangoChoices):
        github = ChoiceItem('gh')

    remote_id = models.IntegerField()
    login = models.TextField()
    name = models.TextField(blank=True, default='')
    type = models.CharField(max_length=1, choices=OwnerType.choices)
    url = models.URLField()
    avatar_url = models.URLField(null=True)
    source = models.CharField(max_length=2, choices=Source.choices)

    def __str__(self):
        return '<Owner name={} type={}>'.format(self.name, self.type)