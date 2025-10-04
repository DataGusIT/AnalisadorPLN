# Em core/forms.py

from django import forms
from .models import Candidato, ConfiguracaoExtracao

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        # Vamos pedir apenas o arquivo no formulário inicial.
        # Os outros campos serão preenchidos pelo spaCy.
        fields = ('curriculo_original',)

# --- NOVO FORMULÁRIO ADICIONADO AQUI ---
class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoExtracao
        # Lista os campos que queremos que virem checkboxes
        fields = [
            'extrair_experiencia',
            'extrair_habilidades',
            'extrair_formacao',
            'extrair_idiomas'
        ]