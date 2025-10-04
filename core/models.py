# Em core/models.py

from django.db import models

class Candidato(models.Model):
    # Campos existentes...
    curriculo_original = models.FileField(upload_to='curriculos/')
    texto_do_curriculo = models.TextField(blank=True, null=True)
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    habilidades = models.TextField(blank=True, null=True)
    experiencia = models.TextField(blank=True, null=True)
    
    # --- NOVOS CAMPOS ADICIONADOS AQUI ---
    formacao_academica = models.TextField(blank=True, null=True, verbose_name="Formação Acadêmica")
    idiomas = models.TextField(blank=True, null=True, verbose_name="Idiomas")
    
    data_de_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_completo or f"Candidato ID {self.id}"

    class Meta:
        ordering = ['-data_de_upload']

# --- NOVO MODELO ADICIONADO AQUI ---
class ConfiguracaoExtracao(models.Model):
    """
    Um modelo para armazenar as configurações globais de extração.
    Usaremos um padrão Singleton (garantir que exista apenas uma linha nesta tabela).
    """
    extrair_experiencia = models.BooleanField(default=True, verbose_name="Extrair Experiência Profissional")
    extrair_habilidades = models.BooleanField(default=True, verbose_name="Extrair Competências e Habilidades")
    extrair_formacao = models.BooleanField(default=True, verbose_name="Extrair Formação Acadêmica")
    extrair_idiomas = models.BooleanField(default=True, verbose_name="Extrair Idiomas")

    def __str__(self):
        return "Configurações de Extração"

    class Meta:
        verbose_name_plural = "Configurações de Extração"