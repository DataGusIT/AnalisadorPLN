# services.py
import spacy
import re

try:
    nlp = spacy.load("pt_core_news_md")  # Usa o modelo médio
except OSError:
    try:
        nlp = spacy.load("pt_core_news_sm")  # Fallback para o modelo pequeno
        print("AVISO: Usando modelo pequeno. Para melhor desempenho, instale:")
        print("python -m spacy download pt_core_news_md")
    except OSError:
        print("ERRO: Nenhum modelo do SpaCy encontrado.")
        nlp = None

# Mini-dicionário de palavras ofensivas
CORE_OFFENSIVE = {
    "puta", "fdp", "caralho", "porra", "merda", 
    "cu", "foder", "vsf", "krl", "pqp", "bosta",
    "arrombado", "desgraça", "inferno"
}


def analisar_toxicidade(texto):
    """
    Sistema híbrido inteligente de detecção
    """
    if not texto or len(texto.strip()) < 5:
        return None
    
    texto_lower = texto.lower()
    alertas = []
    confianca_total = 0
    
    # Verificação direta de palavras ofensivas
    palavras_encontradas = []
    for palavra in CORE_OFFENSIVE:
        padrao = r'\b' + re.escape(palavra) + r'\b'
        if re.search(padrao, texto_lower):
            palavras_encontradas.append(palavra)
            confianca_total += 0.9
    
    if palavras_encontradas:
        alertas.append("palavra_ofensiva_core")
    
    # Padrões regex agressivos
    padroes = {
        r'\bv[aá]i?\s+(?:s[ei]|t[ei])\s+(?:foder|ferrar|lascar)': 0.9,
        r'\b(?:filho|filha)\s+d[aeo]\s+(?:puta|rapariga)': 0.95,
        r'(.)\1{5,}': 0.3,
        r'\barrombad[ao]s?\b': 0.85
    }
    
    for padrao, peso in padroes.items():
        if re.search(padrao, texto_lower):
            alertas.append("padrao_agressivo")
            confianca_total += peso
    
    # Verificação de contexto positivo
    palavras_positivas = {
        'gosto', 'adoro', 'amo', 'interessante', 'legal', 'bacana',
        'jogo', 'game', 'culinária', 'cozinhar', 'arte', 'música',
        'esporte', 'tecnologia', 'programação', 'desenho', 'criar'
    }
    
    palavras_no_texto = set(texto_lower.split())
    contexto_positivo = len(palavras_no_texto.intersection(palavras_positivas))
    
    if contexto_positivo >= 2:
        confianca_total *= 0.3
    
    if confianca_total >= 0.9:
        return {
            'detectado': True,
            'confianca': min(confianca_total, 1.0),
            'tipos': list(set(alertas)),
            'quantidade': len(alertas),
            'palavras': palavras_encontradas if palavras_encontradas else None,
            'mensagem': 'Detectamos linguagem inadequada ou comportamento suspeito em seu texto.'
        }
    
    return None


def extrair_conceitos_principais(doc):
    """
    Extrai os conceitos mais importantes do texto
    """
    # Tokens importantes: substantivos, verbos e adjetivos
    tokens_importantes = [
        token for token in doc 
        if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN']
        and not token.is_stop 
        and len(token.text) > 2
    ]
    
    # Chunks nominais (frases como "inteligência artificial")
    chunks = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    
    return tokens_importantes, chunks


def suggest_professions(text: str) -> tuple:
    """
    Versão INTELIGENTE com análise semântica usando apenas SpaCy
    """
    # Verifica toxicidade
    deteccao = analisar_toxicidade(text)
    if deteccao:
        return ([], deteccao)
    
    if not nlp:
        return ([], None)

    # Processa o texto do usuário
    doc_usuario = nlp(text.lower())
    
    # Extrai conceitos principais
    tokens_importantes, chunks = extrair_conceitos_principais(doc_usuario)
    
    # Se não extraiu nada relevante
    if len(tokens_importantes) == 0 and len(chunks) == 0:
        return ([], None)

    from .professions import PROFESSION_KEYWORDS, PROFESSION_DESCRIPTIONS
    
    scores = {}
    
    for profession, keywords in PROFESSION_KEYWORDS.items():
        score = 0
        
        # ========================================
        # MÉTODO 1: Match direto de palavras-chave
        # ========================================
        user_lemmas = {token.lemma_ for token in tokens_importantes}
        user_text_lower = text.lower()
        
        # Match de lemmas
        direct_matches = len(user_lemmas.intersection(keywords))
        score += direct_matches * 3.0  # AUMENTADO: 3 pontos por match direto
        
        # Match de chunks nominais
        for chunk in chunks:
            if chunk in keywords or any(keyword in chunk for keyword in keywords):
                score += 2.5
        
        # ========================================
        # MÉTODO 2: Similaridade semântica com descrição
        # ========================================
        if profession in PROFESSION_DESCRIPTIONS and doc_usuario.has_vector:
            desc_text = PROFESSION_DESCRIPTIONS[profession]
            doc_profissao = nlp(desc_text)
            
            # Similaridade geral do documento
            if doc_profissao.has_vector:
                similaridade_doc = doc_usuario.similarity(doc_profissao)
                # Só adiciona se a similaridade for significativa
                if similaridade_doc > 0.3:
                    score += similaridade_doc * 15  # AUMENTADO: Até 15 pontos
        
        # ========================================
        # MÉTODO 3: Similaridade token-a-token (mais preciso)
        # ========================================
        for token_usuario in tokens_importantes:
            if token_usuario.has_vector:
                max_sim_token = 0
                best_match = None
                
                for keyword in keywords:
                    keyword_doc = nlp(keyword)
                    if keyword_doc.has_vector:
                        sim = token_usuario.similarity(keyword_doc)
                        if sim > max_sim_token:
                            max_sim_token = sim
                            best_match = keyword
                
                # Threshold ajustado para ser mais seletivo
                if max_sim_token > 0.65:  # Aumentado de 0.6 para 0.65
                    score += max_sim_token * 2.5
        
        # ========================================
        # MÉTODO 4: Penalização por falta de contexto
        # ========================================
        # Se a pontuação for baixa E o texto for curto, penaliza ainda mais
        if score > 0 and score < 5 and len(text.split()) < 5:
            score *= 0.5  # Reduz pela metade
        
        if score > 0:
            scores[profession] = round(score, 2)

    # Ordena e retorna top 5
    sorted_professions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # FILTRO FINAL: Remove profissões com score muito baixo
    sorted_professions = [(prof, score) for prof, score in sorted_professions if score >= 3.0]

    return (sorted_professions, None)