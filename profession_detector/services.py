# profession_detector/services.py
import spacy
from .professions import PROFESSION_KEYWORDS

# Dicionário de palavrões
PALAVRAS_INADEQUADAS = {
    # Palavrões comuns
    "merda", "porra", "caralho", "cacete", "droga", "inferno",
    "desgraça", "maldito", "idiota", "burro", "estúpido",
    
    # Xingamentos
    "fdp", "filha da puta", "filho da puta", "vai se foder", "va se foder",
    "vai tomar no cu", "cu", "puta", "viado", "bicha",
    
    # Palavras ofensivas
    "bosta", "cuzão", "cuzao", "babaca", "otário", "otario", "imbecil", "cretino",
    "piranha", "vagabundo", "safado", "desgraçado", "desgracado",
    
    # Gírias ofensivas
    "arrombado", "escroto", "vsf", "vtmnc", "krl", "caralho",
    "pqp", "lixo", "retardado", "foda-se", "foda se", "foder"
}

# Carrega o modelo do SpaCy uma vez para otimizar o desempenho.
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("Modelo 'pt_core_news_sm' do SpaCy não encontrado.")
    print("Execute: python -m spacy download pt_core_news_sm")
    nlp = None


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
            'palavras': palavras_detectadas[:3],
            'tem_mais': len(palavras_detectadas) > 3
        }
    
    return None


def suggest_professions(text: str) -> tuple:
    """
    Analisa um texto de hobbies e retorna:
    - Uma lista ordenada de profissões sugeridas
    - Um dicionário com informações sobre palavrões (ou None)
    
    Retorna: (lista_sugestões, aviso_palavrao)
    """
    
    # PRIMEIRO: Verifica linguagem inapropriada
    deteccao = detectar_linguagem_inapropriada(text)
    
    if deteccao:
        # Se detectou palavrões, retorna lista vazia e o aviso
        return ([], deteccao)
    
    # Se não há palavrões E o modelo SpaCy não está carregado
    if nlp is None:
        return ([], None)

    # Processa normalmente com SpaCy
    doc = nlp(text.lower())

    # Extrai os "lemas" (forma base da palavra) de substantivos, verbos e adjetivos
    user_keywords = {
        token.lemma_ for token in doc 
        if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and not token.is_stop and not token.is_punct
    }

    # Calcula a pontuação de cada profissão
    scores = {}
    for profession, keywords in PROFESSION_KEYWORDS.items():
        common_keywords = user_keywords.intersection(keywords)
        if common_keywords:
            scores[profession] = len(common_keywords)

    # Ordena as profissões da maior para a menor pontuação
    sorted_professions = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    return (sorted_professions, None)