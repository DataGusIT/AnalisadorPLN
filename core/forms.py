# Em core/forms.py

from django import forms
from .models import Candidato

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        # Vamos pedir apenas o arquivo no formulário inicial.
        # Os outros campos serão preenchidos pelo spaCy.
        fields = ('curriculo_original',)