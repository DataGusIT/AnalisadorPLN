# Em core/views.py

import spacy
from spacy.matcher import PhraseMatcher
import fitz  # PyMuPDF
import docx
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CandidatoForm
from .models import Candidato
import re
from django.contrib import messages

# Carregue o modelo do spaCy uma vez quando o servidor iniciar
nlp = spacy.load("pt_core_news_lg")

# --- FUNÇÃO AUXILIAR MELHORADA PARA EXTRAIR TEXTO ---
def extrair_texto_de_arquivo(caminho_arquivo):
    """Extrai texto de arquivos PDF ou DOCX."""
    texto = ""
    try:
        if caminho_arquivo.lower().endswith('.pdf'):
            with fitz.open(caminho_arquivo) as doc:
                for pagina in doc:
                    texto += pagina.get_text()
        elif caminho_arquivo.lower().endswith('.docx'):
            doc = docx.Document(caminho_arquivo)
            for paragrafo in doc.paragraphs:
                texto += paragrafo.text + "\n"
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
    return texto

# --- FUNÇÃO AUXILIAR SUPERIOR PARA EXTRAIR SEÇÕES ---
def extrair_secao(texto, titulos_secao):
    """
    Extrai o texto de uma seção específica do currículo de forma mais robusta.
    - `titulos_secao`: Uma lista de possíveis nomes para a seção (ex: ["Experiência", "Histórico Profissional"]).
    """
    # Cria um padrão regex que busca qualquer um dos títulos, ignorando maiúsculas/minúsculas.
    # Ex: (Experiência Profissional|Histórico Profissional)
    padrao_titulos = "|".join([re.escape(titulo) for titulo in titulos_secao])
    
    # O padrão busca pelo título no início de uma linha, captura tudo até encontrar
    # o próximo padrão que parece ser um título de seção ou o fim do documento.
    padrao = re.compile(
        rf'^\s*({padrao_titulos})\s*[:\n](.*?)(?=\n\s*[A-ZÀ-Ú][a-zà-ú\s]+[:\n]|\Z)',
        re.IGNORECASE | re.DOTALL | re.MULTILINE
    )
    
    match = padrao.search(texto)
    if match:
        # Retorna o grupo 2, que é o conteúdo da seção, limpando espaços extras.
        return match.group(2).strip()
    return None

# --- A NOVA E MAIS INTELIGENTE FUNÇÃO DE PROCESSAMENTO ---
def processar_curriculo_com_spacy(texto):
    doc = nlp(texto)
    
    # --- 1. Extração de Contato (Regex, que já estava boa) ---
    email = None
    telefone = None
    
    match_email = re.search(r'[\w\.-]+@[\w\.-]+', texto)
    if match_email:
        email = match_email.group(0)
        
    match_telefone = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', texto)
    if match_telefone:
        telefone = match_telefone.group(0)

    # --- 2. Extração de Nome (Mais Robusta) ---
    nome = None
    # Procura por uma entidade "Pessoa" (PER) nos primeiros 300 caracteres do CV.
    # Nomes geralmente estão no topo.
    for entidade in nlp(texto[:300]).ents:
        if entidade.label_ == "PER":
            nome = entidade.text
            break # Pega o primeiro que encontrar no topo.
    
    # --- 3. Extração de Competências (MUITO MELHORADA com PhraseMatcher) ---
    SKILLS_LIST = [
        # Linguagens & Banco de Dados
        'python', 'sql', 'postgresql', 'mysql', 'sqlite', 'java', 'javascript', 'typescript', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'html', 'css', 'sass', 'mongodb', 'redis',
        # Frameworks & Bibliotecas
        'django', 'flask', 'fastapi', 'react', 'vue', 'angular', 'node.js', 'express.js', 'jquery', '.net', 'spring boot', 'laravel', 'ruby on rails', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        # Ferramentas & Tecnologias
        'git', 'github', 'gitlab', 'docker', 'kubernetes', 'jenkins', 'jira', 'linux', 'bash', 'powershell', 'api', 'rest', 'graphql', 'json', 'xml', 'jwt',
        # Cloud
        'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'firebase', 's3', 'ec2', 'lambda',
        # BI & Análise de Dados
        'power bi', 'tableau', 'qlik sense', 'google data studio', 'excel', 'vba', 'machine learning', 'data science', 'etl',
        # Metodologias
        'scrum', 'kanban', 'agile', 'metodologias ágeis'
    ]
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in SKILLS_LIST]
    matcher.add("SKILL_MATCH", patterns)

    habilidades_encontradas = set()
    
    # Primeiro, tentamos encontrar uma seção de habilidades dedicada.
    titulos_habilidades = ["Competências", "Habilidades", "Skills", "Tecnologias", "Conhecimentos"]
    secao_habilidades = extrair_secao(texto, titulos_habilidades)
    
    texto_para_analise_skills = secao_habilidades if secao_habilidades else texto
    doc_skills = nlp(texto_para_analise_skills)
    
    matches = matcher(doc_skills)
    for match_id, start, end in matches:
        skill_text = doc_skills[start:end].text
        habilidades_encontradas.add(skill_text.lower())
        
    habilidades_texto = ', '.join(sorted(list(habilidades_encontradas))) if habilidades_encontradas else None

    # --- 4. Extração de Experiência (Usando a nova função de seção) ---
    titulos_experiencia = ["Experiência Profissional", "Histórico Profissional", "Experiência"]
    experiencia_texto = extrair_secao(texto, titulos_experiencia)
    
    return nome, email, telefone, habilidades_texto, experiencia_texto

# --- VIEW DE UPLOAD (ATUALIZADA PARA CHAMAR A NOVA FUNÇÃO) ---
def upload_curriculo(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            candidato_obj = form.save(commit=False) # Não salva no banco ainda

            caminho_arquivo = candidato_obj.curriculo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)
            
            candidato_obj.texto_do_curriculo = texto_extraido
            
            # Chama a nova função de processamento inteligente
            nome, email, telefone, habilidades, experiencia = processar_curriculo_com_spacy(texto_extraido)
            
            candidato_obj.nome_completo = nome
            candidato_obj.email = email
            candidato_obj.telefone = telefone
            candidato_obj.habilidades = habilidades
            candidato_obj.experiencia = experiencia
            
            candidato_obj.save() # Agora salva tudo de uma vez
            
            return redirect('core:detalhe_candidato', candidato_id=candidato_obj.id)
        else:
            # Se o form não for válido, podemos mostrar os erros
            # (útil para depuração)
            print(form.errors)
            messages.error(request, "Houve um erro no envio do formulário. Tente novamente.")
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
    # CORREÇÃO AQUI: de 'data_upload' para 'data_de_upload'
    candidatos = Candidato.objects.all().order_by('-data_de_upload')
    context = {
        'candidatos': candidatos
    }
    return render(request, 'core/pagina_historico_candidatos.html', context)

def delete_candidato(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    if request.method == 'POST':
        nome_candidato = candidato.nome_completo or f"ID {candidato.id}"
        candidato.delete()
        # Crie a mensagem de sucesso
        messages.success(request, f"A análise para '{nome_candidato}' foi excluída com sucesso.")
        
        # CORREÇÃO AQUI: Adicione o namespace 'core:'
        return redirect('core:historico_candidatos')
        
    # Esta linha é para caso alguém tente acessar a URL de delete via GET, não é mais usada pelo modal.
    return render(request, 'core/delete_confirm_candidato.html', {'candidato': candidato})