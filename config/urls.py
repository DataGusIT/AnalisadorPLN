# Em config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe
from django.conf.urls.static import static # Importe

urlpatterns = [
    path('admin/', admin.site.urls),
    # Mantém as rotas do app de currículos na raiz
    path('', include('core.urls')), 
    # Adiciona as rotas do novo app sob o prefixo 'extrator/'
    path('extrator/', include('extractor.urls')), 
]


# Adicione esta linha no final. Ela serve os arquivos de mídia em modo de desenvolvimento.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)