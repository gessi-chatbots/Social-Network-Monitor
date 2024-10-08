from django.db import models
import uuid


class Document(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, unique=True)
    text = models.TextField()
    datePublished = models.DateField()
    dateCreated = models.DateField(auto_now_add=True)
    url = models.URLField(unique=True, max_length=255)
    author = models.TextField(blank=True, null=True)
    alternateName = models.CharField(blank=True, null=True, max_length=255)
    additionalType = models.CharField(blank=True, null=True, max_length=255)
    plataformName = models.CharField(blank=True, null=True, max_length=255)
    categoryType = models.CharField(blank=True, null=True, max_length=255)
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(text__isnull=False) & models.Q(datePublished__isnull=False) & models.Q(
                    url__isnull=False), name='required_fields')
        ]