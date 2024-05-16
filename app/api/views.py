from rest_framework import viewsets
from app.models import Document
from app.api.serializer import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer