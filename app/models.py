from django.db import models

# Create your models here.

class Document(models.Model):
    text = models.TextField()
    datePublished = models.DateField()
    dateCreated = models.DateField()
    author = models.TextField()
    url = models.URLField()