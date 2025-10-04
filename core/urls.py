# Em core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.upload_curriculo, name='upload_curriculo'),
    path('candidato/<int:candidato_id>/', views.detalhe_candidato, name='detalhe_candidato'),
    path('historico/', views.historico_candidatos, name='historico_candidatos'),
    path('candidato/<int:candidato_id>/delete/', views.delete_candidato, name='delete_candidato'), # NOVA LINHA
]
