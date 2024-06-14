# services/document_service.py
from snmapp.models import Document
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from uuid import uuid4
from django.utils import timezone
from snmapp.models import Document
from django.db import IntegrityError
from rest_framework.response import Response
from snmapp.api.serializer import DocumentSerializer


def search_local(query, limit, from_date=None, to_date=None):
    filters = {}

    if query:
        filters['text__icontains'] = query
    if from_date:
        filters['datePublished__gte'] = from_date
    if to_date:
        filters['datePublished__lte'] = to_date

    documents = Document.objects.filter(**filters)[:limit]
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data, status=200)

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

def save_document_from_params(text, author, date_published, url='', alternate_name='', additional_type=''):
    try:
        document = Document(
            identifier=str(uuid4()),
            text=text,
            datePublished=date_published,
            dateCreated=timezone.now().date(),
            author=author,
            url=url,
            alternateName=alternate_name,
            additionalType=additional_type
        )
        document.save()
        return True, 'Document saved successfully.'
    except IntegrityError:
        return False, 'Document with this identifier already exists.'
    except Exception as e:
        return False, f'An error occurred: {str(e)}'