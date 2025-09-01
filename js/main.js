document.addEventListener('DOMContentLoaded', () => {
  // Set dynamic year if present
  const yearEl = document.getElementById('jaar');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Trigger fade-in on elements
  const fadeElements = document.querySelectorAll('.fade-in');
  fadeElements.forEach((el, idx) => {
    setTimeout(() => {
      el.classList.add('visible');
    }, 200 * idx);
  });
});

