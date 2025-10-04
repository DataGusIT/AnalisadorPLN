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

# --- A NOVA E PODEROSA FUNÇÃO DE PROCESSAMENTO ---
def processar_documento_com_spacy(texto):
    """
    Usa NER, Matcher com regras customizadas e Regex para extrair
    entidades de forma mais inteligente e contextual de documentos.
    """
    doc = nlp(texto)
    matcher = Matcher(nlp.vocab)

    # --- Padrões de Expressão Regular (Regex) ---
    # Padrão para encontrar CNPJ (XX.XXX.XXX/XXXX-XX)
    padrao_cnpj = [{"TEXT": {"REGEX": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"}}]
    # Padrão para encontrar CPF (XXX.XXX.XXX-XX)
    padrao_cpf = [{"TEXT": {"REGEX": r"\d{3}\.\d{3}\.\d{3}-\d{2}"}}]
    # Padrão para encontrar valores em Reais (R$ X.XXX,XX)
    padrao_valor = [{"TEXT": "R$"}, {"IS_PUNCT": True, "OP": "?"}, {"LIKE_NUM": True}]

    # --- Padrões baseados em Tokens para encontrar as partes ---
    # Padrão aprimorado: procura pela palavra-chave e captura o texto na mesma linha.
    # [contratante/contratada] : [qualquer texto até a quebra de linha]
    padrao_contratante = [
        {"LOWER": "contratante"},
        {"IS_PUNCT": True, "OP": "?"}, # Pega os dois pontos ":"
        {"ENT_TYPE": {"IN": ["ORG", "PER"]}, "OP": "+"} # Pega organizações ou pessoas
    ]
    padrao_contratada = [
        {"LOWER": "contratada"},
        {"IS_PUNCT": True, "OP": "?"},
        {"ENT_TYPE": {"IN": ["ORG", "PER"]}, "OP": "+"}
    ]

    # Adiciona os padrões ao Matcher
    matcher.add("CNPJ", [padrao_cnpj])
    matcher.add("CPF", [padrao_cpf])
    matcher.add("VALOR", [padrao_valor])
    matcher.add("CONTRATANTE", [padrao_contratante])
    matcher.add("CONTRATADA", [padrao_contratada])

    matches = matcher(doc)
    entidades_extraidas = []
    textos_ja_adicionados = set() # Para evitar duplicatas

    # Helper para limpar o texto extraído das partes
    def limpar_texto_chave(texto):
        return re.sub(r'^(contratante|contratada)\s*[:\-]?\s*', '', texto, flags=re.IGNORECASE).strip()

    # Processa os resultados do Matcher (nossas regras customizadas)
    for match_id, start, end in matches:
        regra_id_string = nlp.vocab.strings[match_id]
        span = doc[start:end]
        texto_entidade = span.text

        tipo_entidade = ""
        if regra_id_string in ["CONTRATANTE", "CONTRATADA"]:
            tipo_entidade = "Parte do Contrato"
            texto_entidade = limpar_texto_chave(texto_entidade)
        elif regra_id_string == "CNPJ":
            tipo_entidade = "Documento (CNPJ)"
        elif regra_id_string == "CPF":
            tipo_entidade = "Documento (CPF)"
        elif regra_id_string == "VALOR":
            tipo_entidade = "Valor Monetário"

        if texto_entidade and texto_entidade not in textos_ja_adicionados:
            entidades_extraidas.append({'texto': texto_entidade, 'tipo': tipo_entidade})
            textos_ja_adicionados.add(texto_entidade)

    # Processa as entidades genéricas do spaCy (NER)
    # Apenas se não foram capturadas pelas nossas regras mais específicas
    labels_map = {
        "PER": "Pessoa",
        "LOC": "Local",
        "ORG": "Organização",
        "DATE": "Data",
    }
    for entidade in doc.ents:
        if entidade.text not in textos_ja_adicionados:
            label = labels_map.get(entidade.label_)
            if label:
                entidades_extraidas.append({'texto': entidade.text, 'tipo': label})
                textos_ja_adicionados.add(entidade.text)

    return entidades_extraidas


# --- VIEW DE UPLOAD (ATUALIZADA) ---
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento_obj = form.save(commit=False)
            documento_obj.titulo = documento_obj.arquivo_original.name
            
            caminho_arquivo = documento_obj.arquivo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)
            
            # Chama a nova função inteligente
            entidades = processar_documento_com_spacy(texto_extraido)
            
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
        # Agrupa as entidades por tipo para facilitar a exibição
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