# Em core/views.py

import spacy
from spacy.matcher import PhraseMatcher
import fitz  # PyMuPDF
import docx
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CandidatoForm, ConfiguracaoForm
from .models import Candidato, ConfiguracaoExtracao
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

def processar_curriculo_com_spacy(texto):

    # --- INÍCIO DA MODIFICAÇÃO ---
    # Primeiro, pegamos as configurações salvas no banco de dados.
    config, created = ConfiguracaoExtracao.objects.get_or_create(id=1)
    doc = nlp(texto)
    
    # Inicializa todas as variáveis como None
    nome = None
    email = None
    telefone = None
    habilidades_texto = None
    experiencia_texto = None
    formacao_texto = None
    idiomas_texto = None

     # --- Extração de Contato e Nome (LÓGICA CORRIGIDA) ---
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', texto)
    telefone_match = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', texto)
    
    # Extrai o texto AGORA, de forma segura, e armazena na variável final.
    email = email_match.group(0) if email_match else None
    telefone = telefone_match.group(0) if telefone_match else None
    nome = next((ent.text for ent in nlp(texto[:300]).ents if ent.label_ == "PER"), None)

    # --- 2. EXTRAÇÃO DE HABILIDADES SUPER EXPANDIDA ---
    if config.extrair_habilidades:

        # == TECNOLOGIA E DESENVOLVIMENTO ==
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
        
        SKILLS_SEGURANCA = [
            'segurança da informação', 'cibersegurança', 'pentest', 'ethical hacking', 'owasp',
            'firewall', 'vpn', 'criptografia', 'ssl', 'tls', 'oauth', 'jwt', 'saml', 'ldap',
            'kali linux', 'metasploit', 'burp suite', 'wireshark', 'nmap', 'iso 27001', 'lgpd',
            'gdpr', 'sox', 'pci dss', 'compliance', 'auditoria de segurança', 'análise de vulnerabilidades'
        ]
        
        # == NEGÓCIOS E GESTÃO ==
        SKILLS_GESTAO = [
            'gestão de projetos', 'scrum', 'agile', 'kanban', 'pmp', 'prince2', 'pmbok', 'jira',
            'trello', 'asana', 'monday', 'ms project', 'gestão de equipes', 'liderança', 'coaching',
            'mentoria', 'gestão de pessoas', 'rh', 'recrutamento e seleção', 'employer branding',
            'onboarding', 'feedback', 'avaliação de desempenho', 'okr', 'kpi', 'bsc', 'balanced scorecard'
        ]
        
        SKILLS_FINANCAS = [
            'análise financeira', 'modelagem financeira', 'fp&a', 'planejamento financeiro',
            'valuation', 'dcf', 'contabilidade', 'contabilidade gerencial', 'auditoria', 'ifrs',
            'gestão de risco', 'análise de crédito', 'tesouraria', 'controladoria', 'custos',
            'orçamento', 'budget', 'fluxo de caixa', 'demonstrações financeiras', 'balanço patrimonial',
            'sap', 'sap fico', 'oracle', 'totvs', 'protheus', 'oracle netsuite', 'quickbooks',
            'bloomberg terminal', 'thomson reuters', 'mercado de capitais', 'investimentos',
            'renda fixa', 'renda variável', 'derivativos', 'forex', 'cpa-10', 'cpa-20', 'cfa',
            'cea', 'cnpi', 'ancord', 'análise fundamentalista', 'análise técnica'
        ]
        
        SKILLS_MARKETING = [
            'marketing digital', 'seo', 'sem', 'google ads', 'facebook ads', 'instagram ads',
            'linkedin ads', 'tiktok ads', 'mídia paga', 'marketing de conteúdo', 'inbound marketing',
            'outbound marketing', 'growth hacking', 'crm', 'salesforce', 'hubspot', 'rd station',
            'email marketing', 'mailchimp', 'automação de marketing', 'google analytics', 'ga4',
            'tag manager', 'data studio', 'copywriting', 'ux writing', 'branding', 'brand design',
            'social media', 'community management', 'influencer marketing', 'marketing de performance',
            'funil de vendas', 'jornada do cliente', 'personas', 'mvp', 'product-market fit'
        ]
        
        SKILLS_VENDAS = [
            'vendas', 'inside sales', 'vendas consultivas', 'vendas complexas', 'account management',
            'customer success', 'pré-venda', 'pós-venda', 'prospecção', 'cold call', 'negociação',
            'fechamento', 'pipeline', 'forecast', 'spin selling', 'challenger sale', 'bant',
            'sdr', 'bdr', 'ae', 'account executive', 'hunter', 'farmer', 'upsell', 'cross-sell',
            'churn', 'mrr', 'arr', 'ltv', 'cac', 'nps', 'csat'
        ]
        
        # == DESIGN E CRIATIVIDADE ==
        SKILLS_DESIGN = [
            'photoshop', 'illustrator', 'indesign', 'adobe xd', 'figma', 'sketch', 'invision',
            'canva', 'coreldraw', 'after effects', 'premiere', 'final cut', 'davinci resolve',
            'blender', '3ds max', 'maya', 'cinema 4d', 'zbrush', 'substance painter', 'unreal engine',
            'unity', 'ui design', 'ux design', 'ui/ux', 'design thinking', 'prototipagem',
            'wireframe', 'design system', 'design gráfico', 'design editorial', 'identidade visual',
            'motion graphics', 'animação', 'tipografia', 'teoria das cores', 'composição',
            'design de produto', 'design industrial', 'cad', 'autocad', 'solidworks', 'fusion 360'
        ]
        
        # == SAÚDE ==
        SKILLS_SAUDE = [
            'gestão hospitalar', 'gestão de saúde', 'administração hospitalar', 'enfermagem',
            'medicina', 'fisioterapia', 'nutrição', 'psicologia', 'farmácia', 'biomedicina',
            'gestão de pacientes', 'prontuário eletrônico', 'ehr', 'emr', 'pep', 'mv soul', 'tasy',
            'philips tasy', 'wareline', 'senior', 'spdata', 'faturamento médico', 'tiss', 'tuss',
            'cbhpm', 'simpro', 'ans', 'hipaa', 'vigilância sanitária', 'anvisa', 'acreditação',
            'oaa', 'jci', 'ensaios clínicos', 'pesquisa clínica', 'farmacologia', 'farmacovigilância',
            'telemedicina', 'telessaúde', 'home care', 'uti', 'centro cirúrgico', 'emergência'
        ]
        
        # == ENGENHARIA E PRODUÇÃO ==
        SKILLS_ENGENHARIA = [
            'engenharia civil', 'engenharia mecânica', 'engenharia elétrica', 'engenharia de produção',
            'engenharia química', 'engenharia ambiental', 'lean manufacturing', 'six sigma', 'kaizen',
            '5s', 'tpm', 'oee', 'smed', 'kanban produção', 'just in time', 'mrp', 'erp produção',
            'pcp', 'planejamento e controle de produção', 'gestão de estoque', 'logística',
            'supply chain', 'cadeia de suprimentos', 'compras', 'procurement', 'wms', 'tms',
            'gestão de qualidade', 'iso 9001', 'iso 14001', 'iso 45001', 'análise de falhas',
            'fmea', 'controle estatístico', 'cep', 'doe', 'manutenção', 'manutenção preventiva',
            'manutenção preditiva', 'cmms', 'engenharia de processos', 'melhoria contínua'
        ]
        
        # == AGRICULTURA E VETERINÁRIA ==
        SKILLS_AGRO = [
            'agronomia', 'engenharia agrícola', 'agronegócio', 'agricultura', 'pecuária',
            'ciência do solo', 'fertilidade do solo', 'nutrição de plantas', 'fitotecnia',
            'horticultura', 'fruticultura', 'silvicultura', 'gestão de safra', 'planejamento agrícola',
            'agricultura de precisão', 'agricultura 4.0', 'gis', 'sensoriamento remoto', 'drone',
            'vant', 'telemetria', 'mapeamento de solo', 'manejo de pragas', 'controle de pragas',
            'manejo integrado', 'defensivos agrícolas', 'agroquímicos', 'agricultura orgânica',
            'irrigação', 'sistemas de irrigação', 'hidroponia', 'aquaponia', 'biotecnologia agrícola',
            'melhoramento genético', 'sementes', 'máquinas agrícolas', 'mecanização agrícola',
            'veterinária', 'zootecnia', 'sanidade animal', 'nutrição animal', 'reprodução animal',
            'bovinocultura', 'suinocultura', 'avicultura', 'piscicultura', 'apicultura'
        ]
        
        # == EDUCAÇÃO ==
        SKILLS_EDUCACAO = [
            'pedagogia', 'docência', 'educação infantil', 'ensino fundamental', 'ensino médio',
            'ensino superior', 'ead', 'educação a distância', 'moodle', 'blackboard', 'canvas',
            'google classroom', 'metodologias ativas', 'gamificação', 'aprendizagem baseada em projetos',
            'pbl', 'sala de aula invertida', 'bncc', 'didática', 'avaliação educacional',
            'coordenação pedagógica', 'orientação educacional', 'psicopedagogia', 'educação especial',
            'inclusão escolar', 'libras', 'braile', 'tutoria', 'mentoring educacional'
        ]
        
        # == DIREITO ==
        SKILLS_DIREITO = [
            'direito civil', 'direito penal', 'direito trabalhista', 'direito tributário',
            'direito empresarial', 'direito contratual', 'direito administrativo', 'direito constitucional',
            'direito ambiental', 'direito do consumidor', 'direito digital', 'propriedade intelectual',
            'advocacia', 'contencioso', 'consultivo', 'contratos', 'due diligence', 'compliance',
            'compliance tributário', 'compliance trabalhista', 'litigation', 'arbitragem', 'mediação',
            'conciliação', 'processos judiciais', 'peticionamento', 'pje', 'projudi', 'esaj'
        ]
        
        # == ARQUITETURA E URBANISMO ==
        SKILLS_ARQUITETURA = [
            'arquitetura', 'urbanismo', 'paisagismo', 'design de interiores', 'decoração',
            'projeto arquitetônico', 'revit', 'archicad', 'sketchup', 'lumion', 'v-ray',
            'autocad 2d', 'autocad 3d', '3d studio max', 'renderização', 'maquete eletrônica',
            'bim', 'building information modeling', 'projeto luminotécnico', 'conforto térmico',
            'conforto acústico', 'sustentabilidade', 'certificação leed', 'certificação aqua',
            'retrofit', 'restauro', 'patrimônio histórico', 'acessibilidade', 'nbr 9050'
        ]
        
        # == COMUNICAÇÃO ==
        SKILLS_COMUNICACAO = [
            'jornalismo', 'redação', 'edição', 'revisão de textos', 'comunicação corporativa',
            'assessoria de imprensa', 'relações públicas', 'comunicação interna', 'endomarketing',
            'comunicação institucional', 'comunicação integrada', 'planejamento de comunicação',
            'gerenciamento de crise', 'media training', 'press release', 'clipping', 'oratória',
            'apresentações', 'storytelling', 'produção de conteúdo', 'podcast', 'webinar',
            'produção audiovisual', 'roteiro', 'edição de vídeo', 'fotografia', 'fotojornalismo'
        ]
        
        # == IDIOMAS ==
        SKILLS_IDIOMAS = [
            'inglês', 'inglês fluente', 'inglês avançado', 'inglês intermediário', 'english',
            'espanhol', 'espanhol fluente', 'espanhol avançado', 'español',
            'francês', 'français', 'alemão', 'deutsch', 'italiano', 'italiano',
            'mandarim', 'chinês', 'japonês', 'coreano', 'russo', 'árabe',
            'português', 'português brasil', 'português portugal', 'toefl', 'ielts', 'toeic',
            'cambridge', 'dele', 'delf', 'dalf', 'goethe', 'jlpt', 'topik', 'tradução',
            'interpretação', 'interpretação simultânea', 'interpretação consecutiva'
        ]
        
        # == SOFT SKILLS E COMPETÊNCIAS COMPORTAMENTAIS ==
        SKILLS_SOFT = [
            'liderança', 'trabalho em equipe', 'comunicação', 'proatividade', 'criatividade',
            'inovação', 'resolução de problemas', 'pensamento crítico', 'pensamento analítico',
            'inteligência emocional', 'empatia', 'adaptabilidade', 'flexibilidade', 'resiliência',
            'gestão de tempo', 'organização', 'planejamento', 'foco em resultados', 'orientação a dados',
            'tomada de decisão', 'negociação', 'persuasão', 'networking', 'colaboração',
            'autonomia', 'autogestão', 'aprendizado contínuo', 'visão estratégica', 'visão sistêmica'
        ]
        
        # == OUTRAS ÁREAS ==
        SKILLS_TURISMO = [
            'turismo', 'hotelaria', 'gestão hoteleira', 'front desk', 'recepção', 'governança',
            'a&b', 'alimentos e bebidas', 'eventos', 'organização de eventos', 'cerimonial',
            'protocolo', 'agenciamento', 'operadora de turismo', 'guia de turismo', 'amadeus',
            'sabre', 'galileo', 'gds', 'revenue management', 'yield management', 'pms'
        ]
        
        SKILLS_INDUSTRIAL = [
            'soldagem', 'caldeiraria', 'usinagem', 'torno', 'fresa', 'cnc', 'comandos numéricos',
            'leitura e interpretação de desenho', 'metrologia', 'controle dimensional', 'nr-10',
            'nr-12', 'nr-33', 'nr-35', 'trabalho em altura', 'espaço confinado', 'eletricidade',
            'elétrica industrial', 'instrumentação', 'automação industrial', 'clp', 'scada',
            'hidráulica', 'pneumática', 'mecânica industrial'
        ]
        
        SKILLS_ADMINISTRATIVO = [
            'pacote office', 'microsoft office', 'word', 'excel', 'powerpoint', 'outlook', 'access',
            'google workspace', 'google drive', 'google sheets', 'google docs', 'google slides',
            'atendimento ao cliente', 'sac', 'relacionamento com cliente', 'backoffice',
            'arquivo', 'protocolo', 'rotinas administrativas', 'secretariado', 'assistente executivo',
            'gestão de agendas', 'organização de reuniões', 'gestão de viagens', 'expense',
            'reembolso', 'notas fiscais', 'contas a pagar', 'contas a receber', 'conciliação bancária'
        ]

        # Juntamos TODAS as listas em um super dicionário
        MASTER_SKILLS_LIST = (
            SKILLS_PROGRAMACAO + SKILLS_WEB + SKILLS_MOBILE + SKILLS_DADOS + SKILLS_DEVOPS +
            SKILLS_SEGURANCA + SKILLS_GESTAO + SKILLS_FINANCAS + SKILLS_MARKETING + SKILLS_VENDAS +
            SKILLS_DESIGN + SKILLS_SAUDE + SKILLS_ENGENHARIA + SKILLS_AGRO + SKILLS_EDUCACAO +
            SKILLS_DIREITO + SKILLS_ARQUITETURA + SKILLS_COMUNICACAO + SKILLS_IDIOMAS + SKILLS_SOFT +
            SKILLS_TURISMO + SKILLS_INDUSTRIAL + SKILLS_ADMINISTRATIVO
        )

        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(skill) for skill in MASTER_SKILLS_LIST]
        matcher.add("SKILL_MATCH", patterns)
        
        habilidades_encontradas = set()
        
        # Títulos expandidos para a seção de habilidades
        titulos_habilidades = [
            "Competências", "Habilidades", "Skills", "Tecnologias", "Conhecimentos", "Ferramentas",
            "Software", "Hard Skills", "Soft Skills", "Qualificações", "Certificações", "Idiomas",
            "Formação Complementar", "Cursos", "Capacitação Técnica", "Domínios", "Expertise"
        ]
        secao_habilidades = extrair_secao(texto, titulos_habilidades)
        
        # Analisa seção específica ou texto completo
        texto_para_analise = secao_habilidades if secao_habilidades else texto
        doc_analise = nlp(texto_para_analise)
        
        matches = matcher(doc_analise)
        for match_id, start, end in matches:
            habilidades_encontradas.add(doc_analise[start:end].text.strip())

        # == CAMADA 2: DESCOBERTA INTELIGENTE EXPANDIDA ==
        stop_list_skills = {
            "habilidades", "competências", "conhecimentos", "experiência", "idiomas", "formação",
            "educação", "certificações", "cursos", "qualificações", "treinamentos", "capacitação",
            "domínio", "expertise", "proficiência", "nível", "básico", "intermediário", "avançado",
            "fluente", "técnico", "profissional", "acadêmico", "principais", "outras", "adicionais"
        }
        
        if secao_habilidades:
            doc_secao = nlp(secao_habilidades)
            
            # Captura noun chunks (grupos nominais)
            for chunk in doc_secao.noun_chunks:
                texto_chunk = chunk.text.strip()
                if (len(texto_chunk.split()) > 1 or (len(texto_chunk) > 2 and texto_chunk[0].isupper())) \
                    and texto_chunk.lower() not in stop_list_skills:
                    habilidades_encontradas.add(texto_chunk)
            
            # Captura entidades nomeadas (ORG, PRODUCT, etc.)
            for ent in doc_secao.ents:
                if ent.label_ in ["ORG", "PRODUCT", "MISC"] and len(ent.text) > 2:
                    habilidades_encontradas.add(ent.text.strip())
            
            # Captura palavras capitalizadas isoladas (possíveis siglas ou tecnologias)
            for token in doc_secao:
                if token.is_alpha and token.text[0].isupper() and len(token.text) > 1 \
                    and token.text.lower() not in stop_list_skills and not token.is_stop:
                    habilidades_encontradas.add(token.text)

        habilidades_texto = ', '.join(sorted(list(habilidades_encontradas))) if habilidades_encontradas else None
    
     # --- Extração condicional de Experiência ---
    if config.extrair_experiencia:
        titulos_experiencia = [
            "Experiência Profissional", "Histórico Profissional", "Experiência", "Trajetória Profissional",
            "Carreira", "Atuação Profissional", "Experiências", "Histórico"
        ]
        experiencia_texto = extrair_secao(texto, titulos_experiencia)

    # --- Extração condicional de Formação ---
    if config.extrair_formacao:
        titulos_formacao = [
            "Formação Acadêmica", "Educação", "Escolaridade", "Formação", "Histórico Acadêmico"
        ]
        formacao_texto = extrair_secao(texto, titulos_formacao)
    
    # --- Extração condicional de Idiomas ---
    if config.extrair_idiomas:
        titulos_idiomas = ["Idiomas", "Línguas", "Idiomas e Certificações", "Languages"]
        idiomas_texto = extrair_secao(texto, titulos_idiomas)

    return (
        nome,
        email,
        telefone,
        habilidades_texto,
        experiencia_texto,
        formacao_texto,
        idiomas_texto
    )

# --- VIEW DE UPLOAD (ATUALIZADA PARA CHAMAR A NOVA FUNÇÃO) ---
def upload_curriculo(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            candidato_obj = form.save()

            caminho_arquivo = candidato_obj.curriculo_original.path
            texto_extraido = extrair_texto_de_arquivo(caminho_arquivo)
            
            # ATUALIZAÇÃO: Agora desempacotamos 7 valores
            nome, email, telefone, habilidades, experiencia, formacao, idiomas = processar_curriculo_com_spacy(texto_extraido)
            
            candidato_obj.texto_do_curriculo = texto_extraido
            candidato_obj.nome_completo = nome
            candidato_obj.email = email
            candidato_obj.telefone = telefone
            candidato_obj.habilidades = habilidades
            candidato_obj.experiencia = experiencia
            
            # ATUALIZAÇÃO: Salvamos os novos campos
            candidato_obj.formacao_academica = formacao
            candidato_obj.idiomas = idiomas
            
            candidato_obj.save()
            
            return redirect('core:detalhe_candidato', candidato_id=candidato_obj.id)
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

# --- NOVA VIEW ADICIONADA AQUI ---
def configuracao_view(request):
    # Usamos get_or_create para garantir que sempre tenhamos um objeto de configuração.
    # Ele pega o objeto com id=1 ou o cria se não existir.
    config, created = ConfiguracaoExtracao.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações salvas com sucesso!")
            return redirect('core:configuracoes') # Redireciona para a mesma página
    else:
        form = ConfiguracaoForm(instance=config)

    contexto = {
        'form': form
    }
    return render(request, 'core/configuracoes.html', contexto)