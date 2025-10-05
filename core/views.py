# Em core/views.py

import spacy
from spacy.matcher import PhraseMatcher, Matcher
import fitz  # PyMuPDF
import docx
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CandidatoForm, ConfiguracaoForm
from .models import Candidato, ConfiguracaoExtracao
import re
from django.contrib import messages
from collections import defaultdict

# Carregue o modelo do spaCy uma vez quando o servidor iniciar
nlp = spacy.load("pt_core_news_lg")

# --- FUNÇÃO AUXILIAR PARA EXTRAIR TEXTO ---
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

# --- DETECÇÃO INTELIGENTE DE SEÇÕES ---
def detectar_secoes_inteligente(texto):
    """
    Detecta seções do currículo de forma flexível, identificando títulos
    com variações e também usando análise semântica do conteúdo.
    """
    
    # Dicionário com variações de títulos para cada seção
    PADROES_SECOES = {
        'objetivo': [
            r'objetivo\s*(?:profissional)?', r'objetivo\s*de\s*carreira', r'resumo\s*profissional',
            r'sobre\s*mim', r'perfil\s*profissional', r'apresentação', r'summary', r'objective'
        ],
        'experiencia': [
            r'experiência\s*(?:profissional)?', r'histórico\s*profissional', r'trajetória\s*profissional',
            r'experiências', r'atuação\s*profissional', r'vivência\s*profissional',
            r'(?:work\s*)?experience', r'employment\s*history', r'atividades\s*acadêmicas?\s*relevantes?'
        ],
        'formacao': [
            r'formação\s*(?:acadêmica)?', r'educação', r'escolaridade', r'qualificações?\s*acadêmicas?',
            r'titulação', r'graduação', r'education', r'academic\s*background'
        ],
        'habilidades': [
            r'habilidades', r'competências', r'skills', r'conhecimentos', r'tecnologias',
            r'ferramentas', r'capacitações', r'qualificações', r'expertise', r'domínios',
            r'hard\s*skills', r'soft\s*skills', r'principais\s*competências'
        ],
        'idiomas': [
            r'idiomas', r'línguas', r'languages', r'proficiência\s*em\s*idiomas'
        ],
        'cursos': [
            r'cursos', r'certificações', r'certificados', r'treinamentos', r'workshops',
            r'extensões?\s*curriculares?', r'formações?\s*complementares?', r'qualificações?\s*adicionais?',
            r'certifications', r'training'
        ],
        'projetos': [
            r'projetos', r'portfólio', r'trabalhos\s*realizados', r'projects', r'portfolio'
        ]
    }
    
    texto_lower = texto.lower()
    secoes_detectadas = {}
    
    # Encontra todas as posições de possíveis títulos
    posicoes_titulos = []
    
    for tipo_secao, padroes in PADROES_SECOES.items():
        for padrao in padroes:
            # Busca o padrão no início de linha (com possível numeração ou marcador)
            regex_completo = r'(?:^|\n)\s*(?:\d+\.?\s*|[-•*]\s*)?' + padrao + r'\s*:?\s*(?:\n|$)'
            for match in re.finditer(regex_completo, texto_lower, re.MULTILINE | re.IGNORECASE):
                posicoes_titulos.append({
                    'tipo': tipo_secao,
                    'inicio': match.start(),
                    'fim_titulo': match.end(),
                    'titulo_texto': match.group().strip()
                })
    
    # Ordena por posição no texto
    posicoes_titulos.sort(key=lambda x: x['inicio'])
    
    # Extrai o conteúdo de cada seção
    for i, secao in enumerate(posicoes_titulos):
        tipo = secao['tipo']
        inicio_conteudo = secao['fim_titulo']
        
        # Define o fim do conteúdo (início da próxima seção ou fim do texto)
        if i + 1 < len(posicoes_titulos):
            fim_conteudo = posicoes_titulos[i + 1]['inicio']
        else:
            fim_conteudo = len(texto)
        
        conteudo = texto[inicio_conteudo:fim_conteudo].strip()
        
        # Se já existe uma seção desse tipo, concatena (para múltiplas seções similares)
        if tipo in secoes_detectadas:
            secoes_detectadas[tipo] += '\n\n' + conteudo
        else:
            secoes_detectadas[tipo] = conteudo
    
    return secoes_detectadas

# --- EXTRAÇÃO INTELIGENTE DE NOME ---
def extrair_nome_inteligente(texto, doc):
    """
    Extrai o nome do candidato usando múltiplas estratégias:
    1. Entidades PER no início do documento
    2. Primeira linha com padrão de nome
    3. Análise de capitalização
    """
    
    # Estratégia 1: Entidades nomeadas no início (primeiros 500 caracteres)
    doc_inicio = nlp(texto[:500])
    nomes_candidatos = [ent.text for ent in doc_inicio.ents if ent.label_ == 'PER']
    
    if nomes_candidatos:
        # Pega o nome mais longo (geralmente o nome completo)
        return max(nomes_candidatos, key=len)
    
    # Estratégia 2: Primeira linha que parece um nome
    linhas = texto.split('\n')
    for linha in linhas[:10]:  # Verifica as 10 primeiras linhas
        linha = linha.strip()
        
        # Ignora linhas vazias, com email, telefone ou URLs
        if not linha or '@' in linha or 'linkedin' in linha.lower() or 'github' in linha.lower():
            continue
        if re.search(r'\d{4,}', linha):  # Ignora linhas com muitos números
            continue
        
        # Verifica se parece um nome (2-5 palavras capitalizadas)
        palavras = linha.split()
        if 2 <= len(palavras) <= 5 and all(p[0].isupper() for p in palavras if len(p) > 1):
            return linha
    
    # Estratégia 3: Procura por padrão "Nome: XXX" ou similar
    match_nome = re.search(r'(?:nome|name)\s*:?\s*([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)', texto, re.IGNORECASE)
    if match_nome:
        return match_nome.group(1)
    
    return None

# --- EXTRAÇÃO INTELIGENTE DE CONTATOS ---
def extrair_contatos_inteligente(texto):
    """
    Extrai email e telefone com padrões robustos.
    """
    
    # Email: padrão mais abrangente
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', texto)
    email = emails[0] if emails else None
    
    # Telefone: vários formatos brasileiros e internacionais
    padroes_telefone = [
        r'\+?55\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}',  # Brasil com DDI
        r'\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}',  # Brasil sem DDI
        r'\d{4,5}[-\s]?\d{4}',  # Apenas número
        r'\+\d{1,3}\s*\(?\d{1,4}\)?\s*\d{3,4}[-\s]?\d{4}'  # Internacional
    ]
    
    telefone = None
    for padrao in padroes_telefone:
        match = re.search(padrao, texto)
        if match:
            telefone = match.group(0)
            break
    
    return email, telefone

# --- EXTRAÇÃO AVANÇADA DE HABILIDADES ---
def extrair_habilidades_avancada(texto, secoes):
    """
    Extrai habilidades usando:
    1. Lista de skills conhecidas (matcher)
    2. Análise da seção específica de habilidades
    3. Análise de contexto de experiências
    4. Padrões linguísticos
    """
    
    # Lista expandida de habilidades (mantém sua lista original)
    SKILLS_PROGRAMACAO = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust', 'kotlin',
        'swift', 'ruby', 'php', 'perl', 'scala', 'r', 'matlab', 'julia', 'dart', 'objective-c',
        'vb.net', 'visual basic', 'cobol', 'fortran', 'assembly', 'lua', 'groovy', 'elixir',
        'clojure', 'haskell', 'erlang', 'f#', 'bash', 'shell script', 'powershell'
    ]

    SKILLS_WEB = [
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
        'material-ui', 'react', 'react.js', 'vue', 'vue.js', 'angular', 'angularjs', 'svelte',
        'next.js', 'nuxt.js', 'gatsby', 'jquery', 'backbone.js', 'ember.js', 'webpack', 'vite',
        'node.js', 'express', 'nestjs', 'fastify', 'koa', 'asp.net', 'asp.net core', 'spring boot',
        'django', 'flask', 'fastapi', 'rails', 'laravel', 'symfony', 'codeigniter', 'yii'
    ]

    SKILLS_MOBILE = [
        'android', 'ios', 'react native', 'flutter', 'ionic', 'xamarin', 'cordova', 'phonegap',
        'kotlin android', 'swift ios', 'swiftui', 'jetpack compose', 'android studio', 'xcode'
    ]

    SKILLS_DADOS = [
        'sql', 'nosql', 'postgresql', 'mysql', 'mariadb', 'oracle', 'sql server', 'mongodb',
        'redis', 'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'couchdb', 'firebase',
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv',
        'data science', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
        'big data', 'hadoop', 'spark', 'kafka', 'airflow', 'dbt', 'snowflake', 'databricks',
        'power bi', 'tableau', 'looker', 'qlik', 'metabase', 'grafana', 'kibana', 'superset'
    ]

    SKILLS_DEVOPS = [
        'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis ci',
        'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'prometheus', 'nagios', 'datadog',
        'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode', 'cloudflare',
        'linux', 'unix', 'ubuntu', 'centos', 'debian', 'red hat', 'nginx', 'apache', 'tomcat',
        'ci/cd', 'devops', 'sre', 'observabilidade', 'monitoramento', 'iaac', 'gitops'
    ]

    SKILLS_GESTAO = [
        'gestão de projetos', 'scrum', 'agile', 'kanban', 'pmp', 'prince2', 'pmbok', 'jira',
        'trello', 'asana', 'monday', 'ms project', 'gestão de equipes', 'liderança', 'coaching'
    ]

    SKILLS_DESIGN = [
        'photoshop', 'illustrator', 'indesign', 'adobe xd', 'figma', 'sketch', 'invision',
        'canva', 'ui/ux', 'design thinking', 'prototipagem', 'wireframe'
    ]

    SKILLS_MARKETING = [
        'marketing digital', 'seo', 'sem', 'google ads', 'facebook ads', 'social media',
        'copywriting', 'google analytics', 'crm', 'salesforce', 'hubspot'
    ]

    SKILLS_OFFICE = [
        'excel', 'word', 'powerpoint', 'outlook', 'google sheets', 'google docs',
        'pacote office', 'microsoft office', 'google workspace'
    ]

    # Junta todas as habilidades
    TODAS_SKILLS = (
        SKILLS_PROGRAMACAO + SKILLS_WEB + SKILLS_MOBILE + SKILLS_DADOS +
        SKILLS_DEVOPS + SKILLS_GESTAO + SKILLS_DESIGN + SKILLS_MARKETING + SKILLS_OFFICE
    )

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in TODAS_SKILLS]
    matcher.add("SKILL_MATCH", patterns)

    habilidades_encontradas = set()

    # 1. Busca na seção específica de habilidades
    texto_habilidades = secoes.get('habilidades', '')
    if texto_habilidades:
        doc_hab = nlp(texto_habilidades)
        matches = matcher(doc_hab)
        for match_id, start, end in matches:
            habilidades_encontradas.add(doc_hab[start:end].text.lower())

        # Extrai noun chunks e entidades
        for chunk in doc_hab.noun_chunks:
            texto_chunk = chunk.text.strip()
            if len(texto_chunk) > 2 and not chunk.root.is_stop:
                habilidades_encontradas.add(texto_chunk.lower())

        # Procura padrões de lista (ex: "- Python", "• JavaScript")
        linhas = texto_habilidades.split('\n')
        for linha in linhas:
            linha = linha.strip(' -•*\t')
            if linha and len(linha.split()) <= 4:  # Frases curtas
                habilidades_encontradas.add(linha.lower())

    # 2. Busca no texto completo (com menos agressividade)
    doc_completo = nlp(texto)
    matches = matcher(doc_completo)
    for match_id, start, end in matches:
        habilidades_encontradas.add(doc_completo[start:end].text.lower())

    # 3. Busca em contexto de experiências (ex: "utilizando Python", "expertise em AWS")
    texto_exp = secoes.get('experiencia', '')
    if texto_exp:
        padroes_contexto = [
            r'(?:utilizando|usando|com|em|de)\s+([A-Z][a-zA-Z0-9\.\+\#]+)',
            r'(?:conhecimento|experiência|expertise)\s+(?:em|com)\s+([A-Z][a-zA-Z0-9\.\+\#]+)',
            r'(?:desenvolviment[oa]|criação|implementação)\s+(?:de|em|com)\s+([A-Z][a-zA-Z0-9\.\+\#]+)'
        ]

        for padrao in padroes_contexto:
            matches_contexto = re.finditer(padrao, texto_exp)
            for match in matches_contexto:
                skill = match.group(1).strip()
                if len(skill) > 2:
                    habilidades_encontradas.add(skill.lower())

    # Remove stopwords e termos muito genéricos
    stopwords_custom = {
        'de', 'da', 'do', 'para', 'com', 'em', 'por', 'sobre', 'entre',
        'experiência', 'conhecimento', 'habilidade', 'competência', 'trabalho'
    }

    habilidades_filtradas = {
        h for h in habilidades_encontradas
        if h not in stopwords_custom and len(h) > 1
    }

    return ', '.join(sorted(habilidades_filtradas)) if habilidades_filtradas else None

# --- EXTRAÇÃO DE EXPERIÊNCIA COM ANÁLISE TEMPORAL ---
def extrair_experiencia_inteligente(secoes):
    """
    Extrai e organiza experiências profissionais,
    tentando identificar estrutura temporal.
    """

    experiencia_texto = secoes.get('experiencia', '')
    if not experiencia_texto:
        return None

    # Tenta identificar blocos de experiência por datas
    padrao_data = r'\b(\d{4})\b|\b(\d{2}/\d{4})\b|\b(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-z]*\s+\d{4}\b'

    linhas = experiencia_texto.split('\n')
    experiencias_estruturadas = []
    bloco_atual = []

    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        # Se encontra uma data, pode ser início de nova experiência
        if re.search(padrao_data, linha_limpa, re.IGNORECASE):
            if bloco_atual:
                experiencias_estruturadas.append('\n'.join(bloco_atual))
                bloco_atual = []

        bloco_atual.append(linha_limpa)

    if bloco_atual:
        experiencias_estruturadas.append('\n'.join(bloco_atual))

    if experiencias_estruturadas:
        return '\n\n---\n\n'.join(experiencias_estruturadas)

    return experiencia_texto

# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---
def processar_curriculo_com_spacy(texto):
    """
    Função principal que orquestra toda a extração de dados do currículo.
    """

    config, created = ConfiguracaoExtracao.objects.get_or_create(id=1)
    doc = nlp(texto)

    # Detecta as seções do currículo
    secoes = detectar_secoes_inteligente(texto)

    # Extrai informações básicas
    nome = extrair_nome_inteligente(texto, doc)
    email, telefone = extrair_contatos_inteligente(texto)

    # Extrai habilidades (se configurado)
    habilidades_texto = None
    if config.extrair_habilidades:
        habilidades_texto = extrair_habilidades_avancada(texto, secoes)

    # Extrai experiência (se configurado)
    experiencia_texto = None
    if config.extrair_experiencia:
        experiencia_texto = extrair_experiencia_inteligente(secoes)

    # Extrai formação (se configurado)
    formacao_texto = None
    if config.extrair_formacao:
        formacao_texto = secoes.get('formacao', None)
        if not formacao_texto:
            # Fallback: procura por palavras-chave de formação no texto
            padrao_formacao = r'(?:graduação|bacharelado|licenciatura|tecnólogo|mestrado|doutorado|mba)[^\n]{0,200}'
            matches_formacao = re.findall(padrao_formacao, texto, re.IGNORECASE)
            if matches_formacao:
                formacao_texto = '\n'.join(matches_formacao)

    # Extrai idiomas (se configurado)
    idiomas_texto = None
    if config.extrair_idiomas:
        idiomas_texto = secoes.get('idiomas', None)
        if not idiomas_texto:
            # Fallback: procura por padrões de idiomas
            idiomas_conhecidos = ['inglês', 'espanhol', 'francês', 'alemão', 'italiano', 'mandarim', 'japonês']
            idiomas_encontrados = []
            for idioma in idiomas_conhecidos:
                padrao = rf'\b{idioma}\b[^\n]{{0,50}}'
                matches = re.findall(padrao, texto, re.IGNORECASE)
                if matches:
                    idiomas_encontrados.extend(matches)

            if idiomas_encontrados:
                idiomas_texto = '\n'.join(idiomas_encontrados)

    return (nome, email, telefone, habilidades_texto, experiencia_texto,
            formacao_texto, idiomas_texto)

# --- VIEW DE UPLOAD ---
def upload_curriculo(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            candidato_obj = form.save()

            caminho_arquivo = candidato_obj.curriculo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)

            nome, email, telefone, habilidades, experiencia, formacao, idiomas = processar_curriculo_com_spacy(texto_extraido)

            candidato_obj.texto_do_curriculo = texto_extraido
            candidato_obj.nome_completo = nome
            candidato_obj.email = email
            candidato_obj.telefone = telefone
            candidato_obj.habilidades = habilidades
            candidato_obj.experiencia = experiencia
            candidato_obj.formacao_academica = formacao
            candidato_obj.idiomas = idiomas

            candidato_obj.save()

            return redirect('core:detalhe_candidato', candidato_id=candidato_obj.id)
    else:
        form = CandidatoForm()

    return render(request, 'core/upload_curriculo.html', {'form': form})


def detalhe_candidato(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)

    habilidades_lista = []
    if candidato.habilidades:
        habilidades_lista = [h.strip() for h in candidato.habilidades.split(',')]

    contexto = {
        'candidato': candidato,
        'habilidades_lista': habilidades_lista,
    }

    return render(request, 'core/detalhe_candidato.html', contexto)

def historico_candidatos(request):
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
        messages.success(request, f"A análise para '{nome_candidato}' foi excluída com sucesso.")
        return redirect('core:historico_candidatos')

    return render(request, 'core/delete_confirm_candidato.html', {'candidato': candidato})

def configuracao_view(request):
    config, created = ConfiguracaoExtracao.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações salvas com sucesso!")
            return redirect('core:configuracoes')
    else:
        form = ConfiguracaoForm(instance=config)

    contexto = {
        'form': form
    }
    return render(request, 'core/configuracoes.html', contexto)