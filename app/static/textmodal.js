document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('textModal');
  if (!modal) return;
  const pre = modal.querySelector('.modal-pre');
  const download = document.getElementById('modal-download');

  modal.addEventListener('show.bs.modal', event => {
    const trigger = event.relatedTarget;
    if (!trigger) return;
    const text = trigger.getAttribute('data-content') || '';
    const dl = trigger.getAttribute('data-download') || '#';
    pre.textContent = text;
    download.href = dl;
  });
});
