# Em extractor/views.py

import spacy
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DocumentoForm
from .models import Documento
from core.views import extrair_texto_de_arquivo
from spacy.matcher import Matcher
from django.contrib import messages

# Carrega o modelo do spaCy
nlp = spacy.load("pt_core_news_lg")


# --- FUNÇÃO DE PROCESSAMENTO INTELIGENTE (A VERSÃO ATUALIZADA) ---
def processar_documento_com_spacy(texto):
    """
    Usa o NER do spaCy e um Matcher com regras customizadas para extrair
    entidades de forma mais inteligente e contextual.
    """
    doc = nlp(texto)
    matcher = Matcher(nlp.vocab)

    # Padrão 1: Encontrar a CONTRATANTE
    padrao_contratante = [
        {"TEXT": "CONTRATANTE"},
        {"IS_PUNCT": True, "OP": "?"},
        {"POS": "PROPN", "OP": "+"},
        {"POS": "PROPN", "OP": "+", "OP": "?"},
    ]

    # Padrão 2: Encontrar a CONTRATADA
    padrao_contratada = [
        {"TEXT": "CONTRATADA"},
        {"IS_PUNCT": True, "OP": "?"},
        {"POS": "PROPN", "OP": "+"},
        {"POS": "PROPN", "OP": "+", "OP": "?"},
    ]

    matcher.add("CONTRATANTE_PATTERN", [padrao_contratante])
    matcher.add("CONTRATADA_PATTERN", [padrao_contratada])

    matches = matcher(doc)
    entidades_extraidas = []
    entidades_de_regras = set()

    for match_id, start, end in matches:
        span = doc[start:end]
        regra_id_string = nlp.vocab.strings[match_id]
        
        texto_entidade = doc[start+1:end].text.strip(": ")
        
        tipo_entidade = ""
        if regra_id_string == "CONTRATANTE_PATTERN":
            tipo_entidade = "Parte Contratante"
        elif regra_id_string == "CONTRATADA_PATTERN":
            tipo_entidade = "Parte Contratada"
        
        entidades_extraidas.append({
            'texto': texto_entidade,
            'tipo': tipo_entidade,
        })
        entidades_de_regras.add(texto_entidade)

    stop_list = {"contratante", "contratada", "testemunhas", "contrato de prestação de serviços"}
    labels_map = {
        "PER": "Pessoa / Testemunha",
        "LOC": "Local",
        "ORG": "Outra Organização",
    }

    for entidade in doc.ents:
        if entidade.text not in entidades_de_regras and entidade.text.lower() not in stop_list:
            label = labels_map.get(entidade.label_)
            if label:
                entidades_extraidas.append({
                    'texto': entidade.text,
                    'tipo': label,
                })

    return entidades_extraidas


# --- FUNÇÃO DE UPLOAD (A QUE ESTAVA FALTANDO) ---
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento_obj = form.save()
            caminho_arquivo = documento_obj.arquivo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)
            entidades = processar_documento_com_spacy(texto_extraido)
            documento_obj.texto_do_documento = texto_extraido
            documento_obj.entidades_extraidas = entidades
            documento_obj.save()
            return redirect('extractor:resultado_extracao', documento_id=documento_obj.id)
    else:
        form = DocumentoForm()
        
    return render(request, 'extractor/upload_documento.html', {'form': form})


# --- FUNÇÃO DE RESULTADO (A QUE ESTAVA FALTANDO) ---
def resultado_extracao(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)
    
    entidades_agrupadas = {}
    if documento.entidades_extraidas:
        for entidade in documento.entidades_extraidas:
            tipo = entidade['tipo']
            if tipo not in entidades_agrupadas:
                entidades_agrupadas[tipo] = []
            if entidade['texto'] not in entidades_agrupadas[tipo]:
                entidades_agrupadas[tipo].append(entidade['texto'])

    contexto = {
        'documento': documento,
        'entidades_agrupadas': entidades_agrupadas
    }
    return render(request, 'extractor/resultado_extracao.html', contexto)

def historico_documentos(request):
    documentos = Documento.objects.all() # Pega todos os documentos do banco
    contexto = {
        'documentos': documentos
    }
    return render(request, 'extractor/historico_documentos.html', contexto)

def delete_documento(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)
    if request.method == 'POST':
        titulo_documento = documento.titulo
        documento.delete()
        # Crie a mensagem de sucesso
        messages.success(request, f"O documento '{titulo_documento}' foi excluído com sucesso.")
        return redirect('extractor:historico_documentos')
    # A página de confirmação em HTML não será mais usada
    return render(request, 'extractor/delete_confirm_documento.html', {'documento': documento})