# Em extractor/admin.py

from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_de_upload')
    search_fields = ('titulo', 'texto_do_documento')