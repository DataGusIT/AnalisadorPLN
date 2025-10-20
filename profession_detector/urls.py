from django.urls import path
from . import views

app_name = 'profession_detector' # <-- ADICIONE ESTA LINHA

urlpatterns = [
    path('', views.profession_detector_view, name='profession_detector'),
]