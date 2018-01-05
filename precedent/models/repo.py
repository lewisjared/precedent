from django.db import models
from djchoices import ChoiceItem, DjangoChoices

from precedent.models.base import AddedModifiedModel


class Repo(AddedModifiedModel):
    class Source(DjangoChoices):
        github = ChoiceItem('gh')

    remote_id = models.IntegerField()
    name = models.TextField()
    full_name = models.TextField()
    owner = models.ForeignKey('precedent.Owner', on_delete=models.CASCADE)

    description = models.TextField(null=True, blank=True, default='')
    url = models.URLField()
    source = models.CharField(max_length=2, choices=Source.choices, default=Source.github)

    def __str__(self):
        return '<Repo {}>'.format(self.full_name)
