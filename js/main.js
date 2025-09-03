document.addEventListener('DOMContentLoaded', () => {
  // Set dynamic year if present
  const yearEl = document.getElementById('jaar');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Sticky header shadow on scroll
  const onScroll = () => {
    if (window.scrollY > 8) document.body.classList.add('scrolled');
    else document.body.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Active nav link
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.top-bar nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href && href.endsWith(path)) a.classList.add('active');
  });

  // Performant scroll reveal using IntersectionObserver (fallback to simple)
  // Scope to elements that explicitly opt-in (.fade-in)
  const fadeElements = document.querySelectorAll('.fade-in');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    fadeElements.forEach(el => io.observe(el));
  } else {
    fadeElements.forEach((el, idx) => setTimeout(() => el.classList.add('visible'), 150 * idx));
  }
});
