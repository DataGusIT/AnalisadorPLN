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

    // Função para abrir o modal de exclusão
    function openModal() {
        if (modalBackdrop && deleteModal) {
            modalBackdrop.classList.remove('hidden');
            deleteModal.classList.remove('hidden');
        }
    }

    // Função para fechar o modal de exclusão
    function closeModal() {
        if (modalBackdrop && deleteModal) {
            modalBackdrop.classList.add('hidden');
            deleteModal.classList.add('hidden');
        }
    }

    // Adiciona evento para cada botão de exclusão
    deleteTriggers.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const deleteUrl = this.getAttribute('data-url');
            if (deleteUrl && confirmDeleteForm) {
                confirmDeleteForm.setAttribute('action', deleteUrl);
                openModal();
            }
        });
    });

    // Evento para fechar o modal ao clicar no botão "Cancelar"
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeModal);
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
    const htmlElement = document.documentElement;

    function setTeam(theme) {
        localStorage.setItem('theme', theme);
        htmlElement.setAttribute('data-theme', theme);
        if (themeToggle) {
            themeToggle.checked = theme === 'dark';
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('change', function () {
            const newTheme = this.checked ? 'dark' : 'light';
            setTeam(newTheme);
        });
    }

    function loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (savedTheme) {
            setTeam(savedTheme);
        } else if (prefersDark) {
            setTeam('dark');
        } else {
            setTeam('light');
        }
    }
    loadTheme();

    // --- LÓGICA PARA HEADER DINÂMICO AO ROLAR A PÁGINA ---
    const header = document.querySelector('header');
    function handleScroll() {
        if (header) {
            if (window.scrollY > 10) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    }
    window.addEventListener('scroll', handleScroll);
    handleScroll();

    // --- LÓGICA PARA O MENU HAMBÚRGUER ---
    const menuToggle = document.getElementById('menu-toggle');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const mainNav = document.getElementById('main-nav');

    function openMobileMenu() {
        if (mainNav && modalBackdrop) {
            // Garante que o backdrop esteja visível e com a transição certa
            modalBackdrop.style.transition = 'opacity 0.4s ease';
            modalBackdrop.classList.remove('hidden');

            // Força o navegador a aplicar o "display" antes de iniciar a transição de opacidade
            requestAnimationFrame(() => {
                modalBackdrop.style.opacity = '1';
            });

            mainNav.classList.add('mobile-nav-active');
        }
    }

    function closeMobileMenu() {
        if (mainNav && modalBackdrop && mainNav.classList.contains('mobile-nav-active')) {
            // Previne múltiplos cliques enquanto a animação está rodando
            if (mainNav.classList.contains('is-closing')) {
                return;
            }

            // 1. Adiciona a classe que dispara a animação de saída no CSS
            mainNav.classList.add('is-closing');

            // Faz o backdrop sumir suavemente
            modalBackdrop.style.opacity = '0';

            // 2. Ouve o evento de FIM da animação no menu
            mainNav.addEventListener('animationend', () => {
                // 3. Quando a animação termina, esconde os elementos e limpa as classes/estilos
                mainNav.classList.remove('mobile-nav-active');
                modalBackdrop.classList.add('hidden');

                mainNav.classList.remove('is-closing'); // Limpa a classe de fechamento

                // Limpa o estilo de opacidade para não afetar a próxima abertura
                modalBackdrop.style.opacity = '';

            }, { once: true }); // A opção { once: true } garante que o evento só seja ouvido uma vez
        }
    }

    // Adiciona os event listeners que "conectam" os cliques às funções
    if (menuToggle) {
        menuToggle.addEventListener('click', openMobileMenu);
    }

    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', closeMobileMenu);
    }

    // Evento de clique no fundo (backdrop) para fechar TUDO (modal e menu)
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', function () {
            closeModal();      // Fecha o modal de exclusão se estiver aberto
            closeMobileMenu(); // Fecha o menu mobile se estiver aberto
        });
    }

});