# Em core/admin.py

from django.contrib import admin
from .models import Candidato

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'telefone', 'data_de_upload')
    search_fields = ('nome_completo', 'email', 'habilidades', 'texto_do_curriculo')
    list_filter = ('data_de_upload',)