document.addEventListener('DOMContentLoaded', () => {
  const body = document.getElementById('body');
  const toggle = document.getElementById('dark-toggle');
  const prefersDark = localStorage.getItem('darkMode') !== '0';
  if (prefersDark) {
    body.classList.add('dark');
  }
  toggle.innerText = body.classList.contains('dark') ? 'Light Mode' : 'Dark Mode';
  toggle.addEventListener('click', () => {
    body.classList.toggle('dark');
    const dark = body.classList.contains('dark');
    localStorage.setItem('darkMode', dark ? '1' : '0');
    toggle.innerText = dark ? 'Light Mode' : 'Dark Mode';
  });
});
