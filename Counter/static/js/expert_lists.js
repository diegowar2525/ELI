/*  expert_lists.js  */

document.addEventListener('DOMContentLoaded', () => {

  /* Helpers ---------------------------------------------------------------- */

  const modal       = document.getElementById('expertModal');
  const modalTitle  = document.getElementById('modalTitle');
  const listForm    = document.getElementById('list-form');
  const listIdInput = document.getElementById('list-id');
  const listNameInp = document.getElementById('list-name');

  // End-points (ajusta el prefijo si cambias la ruta en urls.py)
  const routes = {
    create: '/expert_lists/create/',
    update: id => `/expert_lists/${id}/update/`,
    del   : id => `/expert_lists/${id}/delete/`,
  };

  const getCSRF = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  };

  const openModal   = () => modal.classList.remove('hidden');
  window.closeModal = () => modal.classList.add('hidden');

  /* Abrir modal para NUEVA lista ------------------------------------------ */
  window.openNewListModal = (btn) => {
    listForm.dataset.expertId = btn.dataset.expertId;
    listIdInput.value   = '';
    listNameInp.value   = '';
    modalTitle.textContent = 'Nueva Lista de Expertos';
    openModal();
  };

  /* Abrir modal para EDITAR lista ----------------------------------------- */
  document.querySelectorAll('.edit-list-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      listForm.dataset.expertId = btn.dataset.expertId;
      listIdInput.value   = btn.dataset.id;
      listNameInp.value   = btn.dataset.name;
      modalTitle.textContent = 'Editar Lista';
      openModal();
    });
  });

  /* Borrar lista ----------------------------------------------------------- */
  document.querySelectorAll('.delete-list-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!confirm('¿Eliminar esta lista?')) return;

      fetch(routes.del(btn.dataset.id), {
        method : 'POST',
        headers: { 'X-CSRFToken': getCSRF() },
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          document.getElementById(`list-row-${btn.dataset.id}`)?.remove();
        }
      });
    });
  });

  /* Enviar formulario (crear / actualizar) -------------------------------- */
  listForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const listId  = listIdInput.value;
    const expertId = listForm.dataset.expertId;

    const url   = listId ? routes.update(listId) : routes.create;
    const body  = { name: listNameInp.value };
    if (!listId) body.expert_id = expertId;

    fetch(url, {
      method : 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken' : getCSRF(),
      },
      body   : JSON.stringify(body)
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) location.reload();   // refresco rápido
    });
  });

});
