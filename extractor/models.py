# Em extractor/models.py

from django.db import models

class Documento(models.Model):
    titulo = models.CharField(max_length=200, help_text="Um título para fácil identificação do documento.")
    arquivo_original = models.FileField(upload_to='documentos/')
    texto_do_documento = models.TextField(blank=True, null=True, verbose_name="Conteúdo em Texto")
    
    # JSONField é perfeito para guardar dados estruturados, como nossa lista de entidades.
    # Cada entidade será um dicionário, ex: {'texto': 'Google', 'tipo': 'ORG'}
    entidades_extraidas = models.JSONField(blank=True, null=True, verbose_name="Entidades (JSON)")
    
    data_de_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-data_de_upload']