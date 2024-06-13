# services/document_service.py
from snmapp.models import Document
from django.shortcuts import get_object_or_404
from django.db import IntegrityError


def get_document(identifier):
    return get_object_or_404(Document, identifier=identifier)

def update_document(identifier, updated_data):
    document = get_document(identifier)
    allowed_fields = ['text', 'datePublished', 'url', 'author', 'alternateName', 'additionalType']
    for field in allowed_fields:
        if field in updated_data:
            setattr(document, field, updated_data[field])
    document.save()
    return document

def delete_document(identifier):
    document = get_document(identifier)
    document.delete()
    return document
