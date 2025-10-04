// Em static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Lógica para o Modal de Exclusão
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        const modalBackdrop = document.getElementById('modalBackdrop');
        const confirmDeleteForm = document.getElementById('confirmDeleteForm');
        const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
        const deleteModalText = document.getElementById('deleteModalText');

        // Abrir o modal
        document.querySelectorAll('.js-delete-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const url = button.dataset.url;
                const itemName = button.dataset.itemName;

                confirmDeleteForm.action = url;
                deleteModalText.textContent = `Você tem certeza que deseja excluir permanentemente "${itemName}"?`;

                modalBackdrop.classList.remove('hidden');
                deleteModal.classList.remove('hidden');
            });
        });

        // Função para fechar o modal
        const closeModal = () => {
            modalBackdrop.classList.add('hidden');
            deleteModal.classList.add('hidden');
        };

        // Fechar o modal clicando no botão "Cancelar" ou no fundo
        cancelDeleteBtn.addEventListener('click', closeModal);
        modalBackdrop.addEventListener('click', closeModal);
    }

    // Lógica para fechar as mensagens de alerta
    document.querySelectorAll('.alert .close-btn').forEach(button => {
        button.addEventListener('click', () => {
            button.parentElement.style.display = 'none';
        });
    });
});