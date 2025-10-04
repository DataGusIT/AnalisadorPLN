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

def processar_documento_com_spacy(texto):
    doc = nlp(texto)
    entidades = []
    spans_ocupados = []

    # LISTA DE EXCLUSÃO ATUALIZADA com o ruído que encontramos.
    stop_list = {
        "contratante", "contratada", "cláusula", "cláusula primeira", "objeto",
        "preço", "prazo", "serviços", "desenvolvimento", "sr", "sra", "sr(a", "brasileiro(a)",
        "testemunhas", "contrato de prestação de serviços"
    }

    def adicionar_entidade(span, tipo, is_ner=False):
        for inicio, fim in spans_ocupados:
            if span.start_char >= inicio and span.end_char <= fim: return
            if span.start_char < fim and span.end_char > inicio: return
        
        texto_limpo = span.text.strip()
        if is_ner and texto_limpo.lower() in stop_list: return
        
        # Ignora entidades muito curtas ou que são apenas pontuação
        if len(texto_limpo) < 2 or texto_limpo in ".,:;": return

        entidades.append({'texto': texto_limpo, 'tipo': tipo})
        spans_ocupados.append((span.start_char, span.end_char))

    # --- CAMADA 1: Regex (Continua igual, é muito confiável) ---
    for match in re.finditer(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", doc.text):
        span = doc.char_span(match.start(), match.end(), label="CNPJ")
        if span: adicionar_entidade(span, "Documento (CNPJ)")
    for match in re.finditer(r"\d{3}\.\d{3}\.\d{3}-\d{2}", doc.text):
        span = doc.char_span(match.start(), match.end(), label="CPF")
        if span: adicionar_entidade(span, "Documento (CPF)")
    for match in re.finditer(r"R\$\s?[\d\.,]+", doc.text):
        span = doc.char_span(match.start(), match.end(), label="VALOR")
        if span: adicionar_entidade(span, "Valor Monetário")

    # --- CAMADA 2: Regras de Contexto (O GRANDE APRIMORAMENTO) ---
    matcher = Matcher(nlp.vocab)
    # PADRÃO "GULOSO": Agora inclui Adjetivos (ADJ) e Adposições (ADP, como "de", "da").
    # Isso permite capturar "TechSolutions Inovação LTDA" e "João da Silva Consultoria".
    padrao_parte = [
        {"LOWER": {"IN": ["contratante", "contratada"]}},
        {"IS_PUNCT": True, "OP": "?"},
        {"POS": {"IN": ["PROPN", "NOUN", "PUNCT", "ADJ", "ADP"]}, "OP": "+"}
    ]
    matcher.add("PARTE_CONTRATO", [padrao_parte])
    
    for match_id, start, end in matcher(doc):
        span = doc[start:end]
        texto_limpo = re.sub(r'^(contratante|contratada)\s*[:\-]?\s*', '', span.text, flags=re.IGNORECASE)
        
        char_start = span.text.find(texto_limpo) + span.start_char
        char_end = char_start + len(texto_limpo)
        span_limpo = doc.char_span(char_start, char_end, label="PARTE")
        
        if span_limpo and any(token.is_alpha for token in span_limpo):
            adicionar_entidade(span_limpo, "Parte do Contrato")

    # --- CAMADA 3: IA Genérica (NER) para capturar o que sobrou ---
    labels_map = {
        "PER": "Pessoa",
        "LOC": "Local",
        "ORG": "Organização",
        "DATE": "Data",
    }
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