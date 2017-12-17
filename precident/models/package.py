from django.db import models
from djchoices import ChoiceItem, DjangoChoices

from precident.models.base import AddedModifiedModel


class Package(AddedModifiedModel):
    class Source(DjangoChoices):
        npm = ChoiceItem('n')
        pypi = ChoiceItem('p')

    class Language(DjangoChoices):
        javascript = ChoiceItem('js')
        python = ChoiceItem('py')

    name = models.TextField()
    description = models.TextField()
    url = models.URLField()
    repo = models.ForeignKey('precident.Repo', on_delete=models.DO_NOTHING)
    language = models.CharField(max_length=2, choices=Language.choices)
    source = models.CharField(max_length=1, choices=Source.choices)

    def __str__(self):
        return '<Package name={} source={}>'.format(self.name, self.source)
