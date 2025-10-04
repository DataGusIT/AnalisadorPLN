# Em core/models.py

from django.db import models

class Candidato(models.Model):
    # Informações que esperamos extrair com o spaCy
    nome_completo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Completo")
    email = models.EmailField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    
    # Campo para guardar o arquivo original do currículo
    # Os arquivos serão salvos em uma pasta 'curriculos' dentro da sua pasta de media
    curriculo_original = models.FileField(upload_to='curriculos/', verbose_name="Arquivo do Currículo")
    
    # Campo de texto para armazenar o conteúdo extraído do arquivo
    texto_do_curriculo = models.TextField(blank=True, null=True, verbose_name="Conteúdo Processado")
    
    # Campos para guardar as informações processadas pelo spaCy
    habilidades = models.TextField(blank=True, null=True, verbose_name="Habilidades Extraídas")
    experiencia = models.TextField(blank=True, null=True, verbose_name="Experiência Profissional")

    # Metadados
    data_de_upload = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Isso ajuda a identificar o objeto na área de admin do Django
        return self.nome_completo or f"Candidato ID {self.id}"

    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ['-data_de_upload']