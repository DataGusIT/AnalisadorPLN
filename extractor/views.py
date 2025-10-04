import spacy
import re # Importação necessária para expressões regulares
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DocumentoForm
from .models import Documento
from core.views import extrair_texto_de_arquivo
from spacy.matcher import Matcher
from django.contrib import messages

# Carrega o modelo do spaCy
nlp = spacy.load("pt_core_news_lg")

# Em extractor/views.py

def processar_documento_com_spacy(texto):
    doc = nlp(texto)
    entidades = []
    spans_ocupados = []

    stop_list = {
        "contratante", "contratada", "cláusula", "cláusulas", "cláusula primeira", 
        "objeto", "valor", "preço", "prazo", "serviços", "desenvolvimento", "sr", "sra", 
        "sr(a", "testemunhas", "contrato de prestação de serviços", "pelo presente instrumento",
        "partes", "instrumento", "presente", "brasileiro", "brasileira", "brasileiro(a)"
    }

    def adicionar_entidade(span, tipo, is_ner=False):
        # Evita sobreposição e duplicatas
        for inicio, fim in spans_ocupados:
            if span.start_char >= inicio and span.end_char <= fim: return
            if span.start_char < fim and span.end_char > inicio: return
        
        texto_limpo = span.text.strip(" .,:;-")
        if is_ner and texto_limpo.lower() in stop_list: return
        if len(texto_limpo) < 2 or texto_limpo in ".,:;": return

        entidades.append({'texto': texto_limpo, 'tipo': tipo})
        spans_ocupados.append((span.start_char, span.end_char))

    # --- CAMADA 1: Regex para dados estruturados (CPF, CNPJ, Valor) ---
    for match in re.finditer(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", doc.text):
        span = doc.char_span(match.start(), match.end())
        if span: adicionar_entidade(span, "Documento (CNPJ)")
    for match in re.finditer(r"\d{3}\.\d{3}\.\d{3}-\d{2}", doc.text):
        span = doc.char_span(match.start(), match.end())
        if span: adicionar_entidade(span, "Documento (CPF)")
    for match in re.finditer(r"R\$\s?[\d\.,]+", doc.text):
        span = doc.char_span(match.start(), match.end())
        if span: adicionar_entidade(span, "Valor Monetário")

    # --- CAMADA 2: EXTRAÇÃO DE CONTEXTO GARANTIDA (OBJETO E PARTES) ---
    
    # Extração robusta do OBJETO
    match_objeto = re.search(r'^\s*objeto.*:\s*(.*)', texto, re.IGNORECASE | re.MULTILINE)
    if match_objeto:
        texto_objeto = match_objeto.group(1).strip()
        char_start = texto.find(texto_objeto)
        if char_start != -1:
            span = doc.char_span(char_start, char_start + len(texto_objeto))
            if span: adicionar_entidade(span, "Objeto do Contrato")

    # Extração GARANTIDA das PARTES com classificação posterior
    for parte_keyword in ['contratante', 'contratada']:
        match_parte = re.search(rf'^\s*{parte_keyword}.*:\s*(.*)', texto, re.IGNORECASE | re.MULTILINE)
        if match_parte:
            texto_parte = match_parte.group(1).strip()
            if not texto_parte: continue

            char_start = texto.find(texto_parte)
            if char_start == -1: continue
            span_parte = doc.char_span(char_start, char_start + len(texto_parte))

            if span_parte:
                doc_snippet = nlp(texto_parte)
                tipo_final = None
                
                # Tenta classificar usando a IA no trecho isolado
                if doc_snippet.ents:
                    entidade_principal = doc_snippet.ents[0]
                    if entidade_principal.label_ == 'ORG':
                        tipo_final = "Parte (Organização)"
                    elif entidade_principal.label_ == 'PER':
                        tipo_final = "Parte (Pessoa)"
                
                # Se a IA falhou, usa um tipo genérico (NUNCA PERDE A INFORMAÇÃO)
                if tipo_final is None:
                    tipo_final = "Parte (Indefinido)"
                
                adicionar_entidade(span_parte, tipo_final)

    # --- CAMADA 3: IA Genérica para capturar o que sobrou (locais, datas, etc.) ---
    labels_map = { "PER": "Pessoa", "LOC": "Local", "ORG": "Organização", "DATE": "Data" }
    for entidade in doc.ents:
        label = labels_map.get(entidade.label_)
        if label:
            adicionar_entidade(entidade, label, is_ner=True)
            
    return entidades

# --- VIEW DE UPLOAD (ATUALIZADA) ---
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento_obj = form.save()

            caminho_arquivo = documento_obj.arquivo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)

            entidades = processar_documento_com_spacy(texto_extraido)

            documento_obj.titulo = documento_obj.arquivo_original.name
            documento_obj.texto_do_documento = texto_extraido
            documento_obj.entidades_extraidas = entidades
            documento_obj.save()
            
            return redirect('extractor:resultado_extracao', documento_id=documento_obj.id)
    else:
        form = DocumentoForm()
        
    return render(request, 'extractor/upload_documento.html', {'form': form})


# --- VIEW DE RESULTADO (ATUALIZADA) ---
def resultado_extracao(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)
    
    entidades_agrupadas = {}
    if documento.entidades_extraidas:
        for entidade in documento.entidades_extraidas:
            tipo = entidade.get('tipo', 'Outros')
            texto = entidade.get('texto')
            if tipo not in entidades_agrupadas:
                entidades_agrupadas[tipo] = []
            if texto not in entidades_agrupadas[tipo]:
                entidades_agrupadas[tipo].append(texto)

    contexto = {
        'documento': documento,
        'entidades_agrupadas': entidades_agrupadas
    }
    return render(request, 'extractor/resultado_extracao.html', contexto)

def historico_documentos(request):
    # CORREÇÃO AQUI: de 'data_upload' para 'data_de_upload'
    documentos = Documento.objects.all().order_by('-data_de_upload')
    context = {
        'documentos': documentos
    }
    return render(request, 'extractor/pagina_historico_documentos.html', context)

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