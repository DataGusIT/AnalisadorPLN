# Em extractor/forms.py

from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        # CORREÇÃO: Adicione a vírgula no final para criar uma tupla.
        fields = ('arquivo_original',)