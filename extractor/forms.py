# Em extractor/forms.py

from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        # Pedimos ao usuário um título e o arquivo.
        fields = ('titulo', 'arquivo_original')