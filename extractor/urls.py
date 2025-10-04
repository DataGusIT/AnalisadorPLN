from django.urls import path
from . import views

app_name = 'extractor'

urlpatterns = [
    path('', views.upload_documento, name='upload_documento'),
    path('resultado/<int:documento_id>/', views.resultado_extracao, name='resultado_extracao'),
    path('historico/', views.historico_documentos, name='historico_documentos'),
    path('documento/<int:documento_id>/delete/', views.delete_documento, name='delete_documento'), # NOVA LINHA
]