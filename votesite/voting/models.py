from django.db import models

# Create your models here.


class Party(models.Model):
    letters = models.CharField('Party Letters', max_length=5, unique=True)
    note = models.ImageField('Party Note Image')
    count = models.PositiveIntegerField(default=0)
