document.addEventListener('DOMContentLoaded', function () {

    // Lógica para fechar os alertas
    const closeButtons = document.querySelectorAll('.alert .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.parentElement.style.opacity = '0';
            setTimeout(() => {
                this.parentElement.style.display = 'none';
            }, 300);
        });
    });

    // Lógica para o Modal de Exclusão
    const modalBackdrop = document.getElementById('modalBackdrop');
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteForm = document.getElementById('confirmDeleteForm');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const deleteTriggers = document.querySelectorAll('.delete-trigger');

    // Função para abrir o modal
    function openModal() {
        modalBackdrop.classList.remove('hidden');
        deleteModal.classList.remove('hidden');
    }

    // Função para fechar o modal
    function closeModal() {
        modalBackdrop.classList.add('hidden');
        deleteModal.classList.add('hidden');
    }

    // Adiciona evento para cada botão de exclusão
    deleteTriggers.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const deleteUrl = this.getAttribute('data-url');
            if (deleteUrl) {
                confirmDeleteForm.setAttribute('action', deleteUrl);
                openModal();
            }
        });
    });

    // Evento para fechar o modal ao clicar no botão "Cancelar"
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeModal);
    }

    // Evento para fechar o modal ao clicar no fundo
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', closeModal);
    }

    // Lógica para mostrar o nome do arquivo selecionado no input
    const fileInput = document.querySelector('.file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const fileInputText = document.querySelector('.file-input-text');
            if (this.files.length > 0) {
                fileInputText.textContent = this.files[0].name;
            } else {
                fileInputText.textContent = 'Clique para escolher um arquivo...';
            }
        });
    }

    // --- LÓGICA PARA O TOGGLE DE TEMA (DARK/LIGHT) ---

    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement; // Seleciona o elemento <html>

    // Função para aplicar o tema e salvar a preferência
    function setTeam(theme) {
        localStorage.setItem('theme', theme); // Salva no storage do navegador
        htmlElement.setAttribute('data-theme', theme); // Aplica o atributo no HTML
        if (themeToggle) {
            themeToggle.checked = theme === 'dark';
        }
    }

    // Evento de clique no toggle
    if (themeToggle) {
        themeToggle.addEventListener('change', function () {
            const newTheme = this.checked ? 'dark' : 'light';
            setTeam(newTheme);
        });
    }

    // Função para carregar o tema na inicialização da página
    function loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        // Verifica se o usuário tem preferência de sistema por tema escuro
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme) {
            // Se houver um tema salvo, usa ele
            setTeam(savedTheme);
        } else if (prefersDark) {
            // Se não houver tema salvo, mas o sistema preferir o escuro, usa o escuro
            setTeam('dark');
        } else {
            // Caso contrário, usa o tema claro como padrão
            setTeam('light');
        }
    }

    // Carrega o tema assim que a página é carregada
    loadTheme();

    // --- LÓGICA PARA HEADER DINÂMICO AO ROLAR A PÁGINA ---
    const header = document.querySelector('header');

    // Função para verificar a posição da rolagem e aplicar a classe
    function handleScroll() {
        if (header) {
            if (window.scrollY > 10) { // Adiciona a classe após rolar 10 pixels
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    }

    // Adiciona o evento de rolagem
    window.addEventListener('scroll', handleScroll);

    // Executa a função uma vez no carregamento para o caso da página já carregar rolada
    handleScroll();



});