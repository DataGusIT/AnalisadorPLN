# views.py
from django.shortcuts import render
from django.contrib import messages

# Dicionário de palavrões (coloque no início do arquivo ou em um arquivo separado)
PALAVRAS_INADEQUADAS = {
    # Palavrões comuns
    "merda", "porra", "caralho", "cacete", "droga", "inferno",
    "desgraça", "maldito", "idiota", "burro", "estúpido",
    
    # Xingamentos
    "fdp", "filha da puta", "filho da puta", "vai se foder", "va se foder",
    "vai tomar no cu", "cu", "puta", "viado", "bicha",
    
    # Palavras ofensivas
    "bosta", "cuzão", "babaca", "otário", "imbecil", "cretino",
    "piranha", "vagabundo", "safado", "desgraçado",
    
    # Gírias ofensivas
    "arrombado", "escroto", "vsf", "vtmnc", "krl",
    "pqp", "lixo", "retardado", "gay" # (se usado pejorativamente)
}

PROFESSION_KEYWORDS = {
    # TECNOLOGIA E COMPUTAÇÃO
    "Desenvolvedor(a) de Software": {
        "programação", "código", "computador", "lógica", "tecnologia", 
        "resolver problemas", "software", "desenvolver", "aplicativo", "jogo",
        "algoritmo", "python", "java", "javascript", "debug", "app", "sistema",
        "web", "mobile", "criar soluções", "inovar", "digital"
    },
    "Cientista de Dados": {
        "dados", "análise", "números", "estatística", "computador", 
        "padrões", "programação", "gráficos", "machine learning", "ia",
        "inteligência artificial", "python", "sql", "visualização", "métricas",
        "big data", "predição", "modelagem", "pesquisa"
    },
    "Engenheiro(a) de Software": {
        "arquitetura", "sistemas", "infraestrutura", "código", "tecnologia",
        "escalabilidade", "performance", "otimização", "cloud", "servidor",
        "banco de dados", "api", "microsserviços", "devops"
    },
    "Designer UX/UI": {
        "interface", "usuário", "experiência", "design", "prototipagem",
        "figma", "wireframe", "visual", "interação", "usabilidade",
        "cores", "tipografia", "layout", "criatividade", "estética"
    },
    "Analista de Segurança da Informação": {
        "segurança", "proteção", "hacker ético", "cibersegurança", "rede",
        "firewall", "criptografia", "vulnerabilidade", "teste de invasão",
        "tecnologia", "prevenir ataques", "computador"
    },
    "Administrador(a) de Redes": {
        "redes", "internet", "servidor", "conexão", "infraestrutura",
        "wi-fi", "configuração", "manutenção", "tecnologia", "suporte"
    },
    "Desenvolvedor(a) de Jogos": {
        "jogos", "games", "entretenimento", "programação", "unity",
        "unreal", "3d", "personagens", "gameplay", "criatividade",
        "animação", "storytelling", "diversão", "imersão"
    },
    "Analista de Sistemas": {
        "sistemas", "análise", "requisitos", "documentação", "processos",
        "negócios", "tecnologia", "soluções", "otimização", "eficiência"
    },

    # DESIGN E ARTES
    "Designer Gráfico": {
        "desenho", "arte", "cores", "criatividade", "visual", "imagem", 
        "ilustração", "criar", "estilo", "pintar", "photoshop", "illustrator",
        "marca", "logotipo", "cartaz", "layout", "composição", "identidade visual"
    },
    "Arquiteto(a)": {
        "prédios", "construção", "design", "espaços", "estruturas",
        "plantas", "criatividade", "urbanismo", "sustentabilidade", "estética",
        "autocad", "3d", "projeto", "inovação", "funcionalidade"
    },
    "Designer de Interiores": {
        "decoração", "ambientes", "móveis", "cores", "espaços",
        "conforto", "estilo", "harmonia", "iluminação", "layout",
        "criatividade", "transformar", "aconchego"
    },
    "Fotógrafo(a)": {
        "fotografia", "câmera", "imagens", "luz", "composição",
        "momentos", "capturar", "criatividade", "visual", "edição",
        "paisagens", "retratos", "arte", "perspectiva"
    },
    "Ilustrador(a)": {
        "desenho", "ilustração", "arte", "criatividade", "personagens",
        "histórias", "visual", "imaginação", "digital", "tradicional",
        "cores", "estilo", "narrativa visual"
    },
    "Animador(a) 3D": {
        "animação", "3d", "movimento", "personagens", "cinema",
        "efeitos especiais", "modelagem", "render", "criatividade",
        "storytelling", "tecnologia", "arte"
    },
    "Diretor(a) de Arte": {
        "criatividade", "visual", "conceito", "campanha", "publicidade",
        "estética", "inovação", "marca", "comunicação", "design",
        "estratégia visual", "arte"
    },

    # SAÚDE E BEM-ESTAR
    "Médico(a)": {
        "saúde", "cuidar", "pessoas", "ciência", "biologia", "ajudar", 
        "hospital", "medicina", "corpo humano", "vida", "diagnóstico",
        "tratamento", "pacientes", "salvar vidas", "anatomia", "doenças"
    },
    "Enfermeiro(a)": {
        "cuidar", "saúde", "pacientes", "hospital", "ajudar",
        "medicação", "tratamento", "suporte", "empatia", "urgência",
        "pessoas", "dedicação", "plantão"
    },
    "Dentista": {
        "dentes", "saúde bucal", "sorriso", "cuidar", "odontologia",
        "tratamento", "limpeza", "prevenção", "clínica", "pacientes"
    },
    "Fisioterapeuta": {
        "reabilitação", "movimento", "corpo", "exercícios", "recuperação",
        "lesões", "saúde", "ajudar", "pacientes", "bem-estar",
        "fisioterapia", "mobilidade"
    },
    "Nutricionista": {
        "alimentação", "saúde", "dieta", "nutrição", "bem-estar",
        "corpo", "emagrecimento", "equilíbrio", "saúde", "alimentos",
        "plano alimentar", "biologia"
    },
    "Psicólogo(a)": {
        "mente", "comportamento", "ajudar", "ouvir", "pessoas", 
        "sentimentos", "terapia", "entender", "emoções", "saúde mental",
        "conversar", "apoio", "ansiedade", "depressão", "autoconhecimento"
    },
    "Psiquiatra": {
        "saúde mental", "medicina", "cérebro", "transtornos", "tratamento",
        "medicação", "terapia", "ajudar", "diagnóstico", "pessoas"
    },
    "Farmacêutico(a)": {
        "medicamentos", "farmácia", "remédios", "saúde", "química",
        "prescrição", "orientação", "tratamento", "cuidado", "manipulação"
    },
    "Veterinário(a)": {
        "animais", "cuidar", "bichos", "saúde", "biologia", "clínica", 
        "pets", "tratamento", "amor aos animais", "cirurgia veterinária",
        "diagnóstico", "cachorro", "gato"
    },
    "Terapeuta Ocupacional": {
        "reabilitação", "independência", "atividades", "ajudar",
        "pacientes", "recuperação", "bem-estar", "adaptação", "qualidade de vida"
    },
    "Fonoaudiólogo(a)": {
        "fala", "comunicação", "voz", "audição", "linguagem",
        "tratamento", "crianças", "reabilitação", "ajudar", "terapia"
    },

    # EDUCAÇÃO
    "Professor(a)": {
        "ensinar", "educação", "alunos", "conhecimento", "escola",
        "aprendizado", "didática", "explicar", "formar", "inspirar",
        "matérias", "crianças", "jovens", "compartilhar"
    },
    "Pedagogo(a)": {
        "educação", "aprendizagem", "crianças", "desenvolvimento",
        "ensino", "escola", "metodologia", "orientação", "formação"
    },
    "Coordenador(a) Pedagógico": {
        "educação", "gestão", "professores", "escola", "currículo",
        "ensino", "planejamento", "orientação", "qualidade"
    },
    "Professor(a) Universitário": {
        "ensino superior", "pesquisa", "universidade", "conhecimento",
        "acadêmico", "ciência", "formar profissionais", "lecionar"
    },

    # ENGENHARIAS
    "Engenheiro(a) Civil": {
        "construção", "prédios", "matemática", "física", "estruturas", 
        "projetar", "obras", "infraestrutura", "concreto", "pontes",
        "edifícios", "cálculo", "segurança"
    },
    "Engenheiro(a) Mecânico": {
        "máquinas", "motores", "mecânica", "projetos", "indústria",
        "manufatura", "sistemas", "automação", "física", "resolver problemas"
    },
    "Engenheiro(a) Elétrico": {
        "eletricidade", "circuitos", "energia", "projetos", "sistemas elétricos",
        "eletrônica", "tecnologia", "instalações", "física", "matemática"
    },
    "Engenheiro(a) de Produção": {
        "processos", "otimização", "indústria", "produtividade", "gestão",
        "qualidade", "logística", "eficiência", "melhorias", "planejamento"
    },
    "Engenheiro(a) Ambiental": {
        "meio ambiente", "sustentabilidade", "natureza", "preservação",
        "água", "solo", "poluição", "ecologia", "consciência ambiental"
    },
    "Engenheiro(a) Químico": {
        "química", "processos", "indústria", "substâncias", "reações",
        "produção", "laboratório", "análise", "transformação"
    },

    # NEGÓCIOS E GESTÃO
    "Administrador(a)": {
        "gestão", "negócios", "empresa", "planejamento", "organização",
        "liderança", "estratégia", "finanças", "recursos", "eficiência"
    },
    "Contador(a)": {
        "números", "finanças", "impostos", "contabilidade", "balanço",
        "matemática", "organização", "empresa", "declaração", "análise financeira"
    },
    "Economista": {
        "economia", "mercado", "finanças", "análise", "investimentos",
        "matemática", "estatística", "políticas", "indicadores", "crescimento"
    },
    "Analista Financeiro": {
        "finanças", "investimentos", "análise", "números", "mercado",
        "orçamento", "planejamento", "rentabilidade", "riscos"
    },
    "Gestor(a) de Recursos Humanos": {
        "pessoas", "talentos", "recrutamento", "equipe", "gestão",
        "treinamento", "desenvolvimento", "cultura organizacional", "benefícios"
    },
    "Empreendedor(a)": {
        "negócio próprio", "inovação", "criar", "empresa", "startup",
        "independência", "riscos", "oportunidades", "visão", "liderança",
        "autonomia", "projeto próprio"
    },
    "Gerente de Projetos": {
        "gestão", "planejamento", "organização", "equipe", "prazos",
        "coordenação", "objetivos", "liderança", "execução", "resultados"
    },
    "Consultor(a) Empresarial": {
        "consultoria", "estratégia", "análise", "soluções", "negócios",
        "melhorias", "processos", "diagnóstico", "orientação"
    },

    # COMUNICAÇÃO E MÍDIA
    "Jornalista": {
        "escrever", "notícias", "comunicação", "histórias", "investigar", 
        "informar", "ler", "reportagem", "mídia", "entrevistas",
        "verdade", "sociedade", "atualidade"
    },
    "Escritor(a)": {
        "escrever", "livros", "histórias", "criatividade", "narrativa",
        "imaginação", "personagens", "literatura", "publicar", "ler",
        "palavras", "romance", "poesia"
    },
    "Publicitário(a)": {
        "propaganda", "criatividade", "campanhas", "comunicação", "marketing",
        "persuasão", "marcas", "ideias", "publicidade", "estratégia"
    },
    "Relações Públicas": {
        "comunicação", "imagem", "público", "eventos", "mídia",
        "relacionamento", "reputação", "estratégia", "networking"
    },
    "Produtor(a) de Conteúdo": {
        "criar conteúdo", "redes sociais", "criatividade", "digital",
        "vídeos", "posts", "engajamento", "comunicação", "storytelling"
    },
    "Social Media": {
        "redes sociais", "instagram", "facebook", "conteúdo", "engajamento",
        "digital", "criatividade", "estratégia", "comunidade", "trends"
    },
    "Apresentador(a) de TV/Rádio": {
        "comunicação", "falar em público", "mídia", "entrevistas",
        "carisma", "programas", "audiência", "transmissão"
    },

    # DIREITO E JUSTIÇA
    "Advogado(a)": {
        "direito", "justiça", "leis", "defender", "tribunal",
        "processos", "causas", "argumentação", "contratos", "ética",
        "sociedade", "direitos"
    },
    "Juiz(a)": {
        "justiça", "leis", "julgamento", "decisões", "tribunal",
        "imparcialidade", "direito", "processos", "sentença"
    },
    "Promotor(a) de Justiça": {
        "justiça", "acusação", "sociedade", "direito penal", "investigação",
        "tribunal", "defender interesses públicos", "leis"
    },
    "Delegado(a)": {
        "investigação", "polícia", "crimes", "justiça", "segurança",
        "inquérito", "resolver casos", "sociedade", "leis"
    },

    # CIÊNCIAS
    "Biólogo(a)": {
        "biologia", "vida", "natureza", "animais", "plantas",
        "pesquisa", "laboratório", "ecossistemas", "células", "ciência",
        "meio ambiente", "evolução"
    },
    "Químico(a)": {
        "química", "substâncias", "reações", "laboratório", "experimentos",
        "moléculas", "análise", "pesquisa", "compostos", "ciência"
    },
    "Físico(a)": {
        "física", "universo", "matemática", "leis naturais", "pesquisa",
        "partículas", "energia", "experimentos", "teoria", "ciência"
    },
    "Astrônomo(a)": {
        "estrelas", "planetas", "universo", "espaço", "telescópio",
        "cosmos", "galáxias", "astronomia", "observação", "ciência"
    },
    "Geólogo(a)": {
        "terra", "rochas", "minerais", "geologia", "natureza",
        "formações", "pesquisa", "campo", "ciência", "planeta"
    },
    "Cientista Ambiental": {
        "meio ambiente", "sustentabilidade", "ecologia", "preservação",
        "pesquisa", "natureza", "impacto ambiental", "ciência"
    },

    # ARTES E ENTRETENIMENTO
    "Ator/Atriz": {
        "teatro", "cinema", "atuação", "personagens", "dramatização",
        "emoção", "palco", "filmes", "séries", "criatividade",
        "expressão", "arte"
    },
    "Músico(a)": {
        "música", "instrumentos", "tocar", "compor", "melodia",
        "ritmo", "criatividade", "shows", "arte", "som",
        "expressão", "cantar"
    },
    "Cantor(a)": {
        "cantar", "voz", "música", "palco", "shows",
        "emoção", "arte", "interpretação", "melodia", "performance"
    },
    "Dançarino(a)": {
        "dança", "movimento", "corpo", "ritmo", "coreografia",
        "expressão", "arte", "palco", "música", "performance"
    },
    "Diretor(a) de Cinema": {
        "cinema", "filmes", "direção", "narrativa", "visual",
        "criatividade", "roteiro", "câmera", "arte", "storytelling"
    },
    "Produtor(a) Musical": {
        "música", "produção", "estúdio", "som", "gravação",
        "criatividade", "tecnologia", "artistas", "mixagem"
    },

    # ESPORTES
    "Atleta Profissional": {
        "esporte", "competição", "treino", "desempenho", "dedicação",
        "disciplina", "corpo", "performance", "campeonatos", "vitória"
    },
    "Treinador(a) Esportivo": {
        "treinar", "esportes", "técnica", "estratégia", "atletas",
        "motivação", "performance", "tática", "ensinar"
    },
    "Educador(a) Físico": {
        "exercícios", "saúde", "corpo", "atividade física", "bem-estar",
        "treino", "movimento", "qualidade de vida", "esportes"
    },
    "Personal Trainer": {
        "treino", "exercícios", "fitness", "corpo", "saúde",
        "motivação", "academia", "resultados", "bem-estar", "personal"
    },

    # GASTRONOMIA
    "Chef de Cozinha": {
        "cozinhar", "gastronomia", "comida", "receitas", "criatividade",
        "sabores", "culinária", "restaurante", "pratos", "temperos",
        "arte culinária"
    },
    "Confeiteiro(a)": {
        "doces", "bolos", "confeitaria", "criatividade", "decoração",
        "sobremesas", "açúcar", "receitas", "saboroso"
    },
    "Barista": {
        "café", "bebidas", "preparo", "arte latte", "cafeteria",
        "criatividade", "sabor", "técnica"
    },

    # SERVIÇOS E OUTROS
    "Piloto(a) de Avião": {
        "voar", "aviação", "aviões", "céu", "viajar",
        "responsabilidade", "tecnologia", "navegação", "comandar"
    },
    "Bombeiro(a)": {
        "salvar vidas", "coragem", "emergências", "incêndios", "resgates",
        "ajudar", "heroísmo", "adrenalina", "segurança", "equipe"
    },
    "Policial": {
        "segurança", "proteger", "lei", "ordem", "sociedade",
        "justiça", "investigação", "patrulha", "coragem"
    },
    "Assistente Social": {
        "ajudar", "pessoas", "sociedade", "vulnerabilidade", "apoio",
        "direitos", "comunidade", "empatia", "políticas sociais"
    },
    "Tradutor(a)/Intérprete": {
        "idiomas", "línguas", "tradução", "comunicação", "bilíngue",
        "culturas", "interpretação", "fluência", "palavras"
    },
    "Bibliotecário(a)": {
        "livros", "leitura", "organização", "conhecimento", "pesquisa",
        "acervo", "catalogação", "literatura", "informação"
    },
    "Guia Turístico": {
        "turismo", "viajar", "história", "cultura", "guiar",
        "lugares", "conhecimento", "pessoas", "comunicação"
    },
    "Comissário(a) de Bordo": {
        "viajar", "aviação", "atendimento", "pessoas", "avião",
        "segurança", "serviço", "hospitalidade", "céu"
    },
    "Estilista/Designer de Moda": {
        "moda", "roupas", "criatividade", "estilo", "tendências",
        "tecidos", "design", "cores", "desfile", "coleções"
    },
    "Cabeleireiro(a)/Hair Stylist": {
        "cabelo", "estilo", "criatividade", "beleza", "transformação",
        "corte", "cor", "salão", "visual", "moda"
    },
    "Maquiador(a)": {
        "maquiagem", "beleza", "criatividade", "cores", "transformação",
        "arte", "rosto", "estilo", "produção"
    },
    "Mecânico(a)": {
        "carros", "motores", "consertar", "máquinas", "ferramentas",
        "mecânica", "veículos", "manutenção", "resolver problemas"
    },
    "Eletricista": {
        "eletricidade", "instalações", "fios", "consertos", "energia",
        "circuitos", "segurança", "técnico", "resolver problemas"
    },
    "Agricultor(a)": {
        "plantação", "terra", "natureza", "colheita", "alimentos",
        "campo", "agricultura", "sustentabilidade", "cultivo"
    },
    "Biólogo(a) Marinho": {
        "oceano", "mar", "vida marinha", "peixes", "pesquisa",
        "mergulho", "ecossistema", "conservação", "água", "biologia"
    },
    "Arqueólogo(a)": {
        "história", "escavações", "civilizações antigas", "descobertas",
        "pesquisa", "artefatos", "passado", "cultura", "mistérios"
    },
    "Paleontólogo(a)": {
        "dinossauros", "fósseis", "história", "escavações", "pesquisa",
        "evolução", "passado", "descobertas", "ossos", "ciência"
    },
}

def detectar_linguagem_inapropriada(texto):
    """
    Detecta palavrões e retorna informações sobre eles
    """
    if not texto:
        return None
    
    texto_lower = texto.lower()
    palavras_detectadas = []
    
    for palavra in PALAVRAS_INADEQUADAS:
        if palavra in texto_lower:
            palavras_detectadas.append(palavra)
    
    if palavras_detectadas:
        return {
            'detectado': True,
            'quantidade': len(palavras_detectadas),
            'palavras': palavras_detectadas[:3],  # Mostra até 3 palavras
            'tem_mais': len(palavras_detectadas) > 3
        }
    
    return None


def detector_profissoes(request):
    suggestions = []
    submitted_text = ""
    aviso_palavrao = None
    
    if request.method == 'POST':
        hobbies = request.POST.get('hobbies', '').strip()
        submitted_text = hobbies
        
        # VERIFICA LINGUAGEM INAPROPRIADA PRIMEIRO
        deteccao = detectar_linguagem_inapropriada(hobbies)
        
        if deteccao:
            # Se detectou palavrões, armazena informações e NÃO processa sugestões
            aviso_palavrao = deteccao
            
            # Opcional: Adiciona mensagem do Django também
            messages.warning(
                request, 
                f"⚠️ Detectamos {deteccao['quantidade']} palavra(s) inadequada(s) em sua resposta. "
                "Por favor, reformule de forma mais adequada."
            )
        else:
            # Se não tem palavrões, processa normalmente
            if hobbies:
                palavras_usuario = set(hobbies.lower().split())
                scores = {}
                
                for profession, keywords in PROFESSION_KEYWORDS.items():
                    match_count = len(palavras_usuario.intersection(keywords))
                    if match_count > 0:
                        scores[profession] = match_count
                
                suggestions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'suggestions': suggestions,
        'submitted_text': submitted_text,
        'aviso_palavrao': aviso_palavrao,  # Passa informações do aviso para o template
    }
    
    return render(request, 'detector_profissoes.html', context)