# Analisador Inteligente de Currículos com IA

> Plataforma de IA para automatizar a triagem de candidatos, extraindo e estruturando informações de currículos (PDF e DOCX) usando Processamento de Linguagem Natural com spaCy e Django.

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)](https://github.com/seu-usuario/analisador-curriculos-ia)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Framework-092E20)](https://www.djangoproject.com/)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5)](https://spacy.io/)

## Sobre o Projeto

O **Analisador Inteligente de Currículos** é uma ferramenta web desenvolvida para otimizar o processo de recrutamento e seleção. A aplicação utiliza o poder do Processamento de Linguagem Natural (PLN) para ler arquivos de currículo, identificar seções de forma inteligente e extrair dados cruciais como informações de contato, experiência profissional, formação acadêmica, habilidades e idiomas.

Construído com Django e a biblioteca spaCy, este projeto transforma documentos não estruturados em dados organizados e prontos para análise, economizando tempo e aumentando a eficiência da equipe de RH.

## ✨ Funcionalidades

### 📂 Upload e Extração de Texto
- **Suporte a Múltiplos Formatos:** Aceita currículos nos formatos mais comuns: **PDF** e **DOCX**.
- **Extração Robusta:** Utiliza `PyMuPDF` e `python-docx` para uma conversão de alta fidelidade do arquivo para texto puro.

### 🧠 Análise com Inteligência Artificial (PLN)
- **Detecção Inteligente de Seções:** Em vez de regras fixas, o sistema usa expressões regulares flexíveis e análise contextual para identificar seções como "Experiência Profissional", "Formação" e "Habilidades", mesmo que os títulos variem.
- **Extração Precisa de Contatos:** Isola de forma confiável o nome completo, e-mail e telefone do candidato.
- **Mapeamento Avançado de Habilidades:** Utiliza um extenso dicionário de competências (programação, DevOps, gestão, design, etc.) e o `PhraseMatcher` do spaCy para identificar e listar as habilidades do candidato.
- **Estruturação de Experiência e Formação:** Organiza o conteúdo das seções de experiência e educação para uma leitura clara.

### 🖥️ Interface Web Completa
- **Página de Upload Intuitiva:** Interface limpa para envio rápido de currículos.
- **Dashboard de Resultados:** Apresenta os dados extraídos de forma organizada e fácil de ler.
- **Histórico de Análises:** Armazena todas as análises realizadas, permitindo consultar candidatos anteriores.
- **Painel de Configurações:** Permite ao usuário habilitar ou desabilitar a extração de seções específicas (experiência, habilidades, etc.), customizando a análise.

## 🖼️ Demonstração Visual

| Página de Upload | Página de Resultados da Análise |
| :---: | :---: |
| ![Página de Upload](link-para-sua-imagem-de-upload-aqui) | ![Página de Resultados](link-para-sua-imagem-de-resultados-aqui) |

## Tecnologias

### Backend
- **Python 3.9+**
- **Django** - Framework web principal

### Processamento de Dados e IA
- **spaCy** - Para Processamento de Linguagem Natural avançado
- **PyMuPDF (fitz)** - Para extração de texto de arquivos PDF
- **python-docx** - Para extração de texto de arquivos DOCX

### Banco de Dados
- **SQLite3** (padrão de desenvolvimento)

## Pré-requisitos

- Python 3.9 ou superior
- Pip (gerenciador de pacotes do Python)

## Instalação

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/seu-usuario/analisador-curriculos-ia.git
    cd analisador-curriculos-ia
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Baixe o modelo de linguagem do spaCy**
    ```bash
    python -m spacy download pt_core_news_sm
    ```

5.  **Aplique as migrações do banco de dados**
    ```bash
    python manage.py migrate
    ```

6.  **Execute a aplicação**
    ```bash
    python manage.py runserver
    ```
    Acesse o sistema em `http://127.0.0.1:8000`.

## Uso

1.  **Acesse a página inicial** e faça o upload de um arquivo de currículo (`.pdf` ou `.docx`).
2.  **Clique em "Enviar para Análise"**. O sistema processará o arquivo em segundo plano.
3.  **Você será redirecionado para a página de detalhes**, onde verá todas as informações extraídas e estruturadas.
4.  Acesse o **Histórico** para ver análises anteriores ou as **Configurações** para personalizar quais dados devem ser extraídos.

## Contribuição

Contribuições são bem-vindas! Se você tem ideias para melhorar a ferramenta, sinta-se à vontade para abrir uma issue ou um Pull Request.

1.  Faça um Fork do projeto
2.  Crie sua Feature Branch (`git checkout -b feature/NovaExtracao`)
3.  Faça Commit de suas mudanças (`git commit -m 'Adiciona extração de certificações'`)
4.  Faça Push para a Branch (`git push origin feature/NovaExtracao`)
5.  Abra um Pull Request

## Suporte

Para suporte técnico ou dúvidas:

-   **Email**: [g.moreno.souza05@gmail.com](mailto:g.moreno.souza05@gmail.com)

## Licença

Este projeto está licenciado sob uma Licença Proprietária.

**Uso Restrito**: Este software é de propriedade exclusiva do autor. Uso comercial ou redistribuição requer autorização expressa.

---

<div align="center">
  Desenvolvido por Gustavo Moreno  
  <br><br>
  <a href="https://www.linkedin.com/in/gustavomoreno05" target="_blank">
    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="24" alt="LinkedIn"/>
  </a>
</div>

