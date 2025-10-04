# Em core/views.py

import spacy
import fitz  # PyMuPDF
import docx
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CandidatoForm
from .models import Candidato
import re
from django.contrib import messages

# Carregue o modelo do spaCy uma vez quando o servidor iniciar
nlp = spacy.load("pt_core_news_lg")

def extrair_texto_de_arquivo(caminho_arquivo):
    """Extrai texto de arquivos PDF ou DOCX."""
    texto = ""
    # Verifica a extensão do arquivo
    if caminho_arquivo.endswith('.pdf'):
        with fitz.open(caminho_arquivo) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    elif caminho_arquivo.endswith('.docx'):
        doc = docx.Document(caminho_arquivo)
        for paragrafo in doc.paragraphs:
            texto += paragrafo.text + "\n"
    return texto

def extrair_secao(texto, titulo_secao):
    """Extrai o texto de uma seção específica do currículo."""
    # Expressão regular para encontrar o título da seção e capturar tudo até o próximo título de seção
    # (considerando que os títulos são palavras no início de uma linha)
    padrao = re.compile(rf'^{re.escape(titulo_secao)}.*?\n(.*?)(?=\n\w+\s*:\n|\Z)', re.IGNORECASE | re.DOTALL | re.MULTILINE)
    match = padrao.search(texto)
    if match:
        return match.group(1).strip()
    return None

def processar_texto_com_spacy(texto):
    doc = nlp(texto)
    
    # --- Extração de Nome, Email, Telefone (código existente) ---
    nome = None
    email = None
    telefone = None
    
    for entidade in doc.ents:
        if entidade.label_ == "PER":
            nome = entidade.text
            break
    
    match_email = re.search(r'[\w\.-]+@[\w\.-]+', texto)
    if match_email:
        email = match_email.group(0)
        
    match_telefone = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', texto)
    if match_telefone:
        telefone = match_telefone.group(0)
    
    # --- NOVA EXTRAÇÃO DE HABILIDADES ---
    # Lista de habilidades que queremos encontrar (pode ser expandida)
    SKILLS = [
        'python', 'sql', 'postgresql', 'power bi', 'excel', 'html', 'css', 
        'git', 'github', 'django', 'javascript', 'react', 'vue', 'angular',
        'api', 'rest', 'docker', 'kubernetes', 'aws', 'azure', 'gcp'
    ]
    
    habilidades_encontradas = set()
    for token in doc:
        # Usamos o .lower() para ignorar maiúsculas/minúsculas
        if token.lemma_.lower() in SKILLS:
            habilidades_encontradas.add(token.lemma_.lower())
    
    habilidades_texto = ', '.join(habilidades_encontradas) if habilidades_encontradas else None

    # --- NOVA EXTRAÇÃO DE EXPERIÊNCIA ---
    titulos_experiencia = ["Experiência Profissional", "Atividades acadêmicas relevantes"]
    experiencia_texto = None
    for titulo in titulos_experiencia:
        secao = extrair_secao(texto, titulo)
        if secao:
            experiencia_texto = secao
            break # Pega a primeira seção que encontrar
    
    return nome, email, telefone, habilidades_texto, experiencia_texto

def upload_curriculo(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            candidato_obj = form.save()

            caminho_arquivo = candidato_obj.curriculo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)
            
            candidato_obj.texto_do_curriculo = texto_extraido
            
            # Agora a função retorna mais valores
            nome, email, telefone, habilidades, experiencia = processar_texto_com_spacy(texto_extraido)
            
            candidato_obj.nome_completo = nome
            candidato_obj.email = email
            candidato_obj.telefone = telefone
            candidato_obj.habilidades = habilidades # Salva as habilidades
            candidato_obj.experiencia = experiencia # Salva a experiência
            
            candidato_obj.save()
            
            # Redireciona para a nova página de detalhes do candidato
            return redirect('detalhe_candidato', candidato_id=candidato_obj.id)
    else:
        form = CandidatoForm()
            
    return render(request, 'core/upload_curriculo.html', {'form': form})

def detalhe_candidato(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    
    # --- INÍCIO DA MODIFICAÇÃO ---
    
    # Prepara a lista de habilidades para o template
    habilidades_lista = []
    if candidato.habilidades:
        # Divide a string 'python,sql,power bi' em uma lista ['python', 'sql', 'power bi']
        # O .strip() remove espaços em branco extras de cada item
        habilidades_lista = [h.strip() for h in candidato.habilidades.split(',')]

    contexto = {
        'candidato': candidato,
        'habilidades_lista': habilidades_lista, # Passa a nova lista para o template
    }
    
    # --- FIM DA MODIFICAÇÃO ---
    
    return render(request, 'core/detalhe_candidato.html', contexto)

def historico_candidatos(request):
    candidatos = Candidato.objects.all() # Pega todos os candidatos do banco
    contexto = {
        'candidatos': candidatos
    }
    return render(request, 'core/historico_candidatos.html', contexto)

def delete_candidato(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    if request.method == 'POST':
        nome_candidato = candidato.nome_completo or f"ID {candidato.id}"
        candidato.delete()
        # Crie a mensagem de sucesso
        messages.success(request, f"A análise para '{nome_candidato}' foi excluída com sucesso.")
        return redirect('historico_candidatos')
    # A página de confirmação em HTML não será mais usada, mas deixamos a lógica por segurança
    return render(request, 'core/delete_confirm_candidato.html', {'candidato': candidato})