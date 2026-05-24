/* Jabbour Electrical Group — Site interactions */
(function () {
  'use strict';

  /* ---- Nav scroll state ---- */
  const nav = document.getElementById('nav');
  let ticking = false;
  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(() => {
        nav.classList.toggle('scrolled', window.scrollY > 40);
        ticking = false;
      });
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Mobile nav ---- */
  const hamburger = document.getElementById('hamburger');
  const navMobile = document.getElementById('nav-mobile');
  function toggleMobileNav(open) {
    hamburger.classList.toggle('active', open);
    hamburger.setAttribute('aria-expanded', String(open));
    navMobile.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  }
  hamburger.addEventListener('click', () => {
    toggleMobileNav(!navMobile.classList.contains('open'));
  });

  /* ---- Smooth scroll & close mobile nav ---- */
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const id = link.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 72, behavior: 'smooth' });
      toggleMobileNav(false);
    });
  });

  /* ---- Scroll reveal ---- */
  const revealObserver = new IntersectionObserver(
    entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    }),
    { threshold: 0.08, rootMargin: '0px 0px -36px 0px' }
  );
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  /* ---- Trigger hero reveals on load (above-fold elements) ---- */
  function revealHero() {
    document.querySelectorAll('.hero .reveal').forEach((el, i) => {
      setTimeout(() => el.classList.add('is-visible'), 120 + i * 100);
    });
  }
  if (document.readyState === 'complete') { revealHero(); }
  else { window.addEventListener('load', revealHero); }

  /* ---- Contact form ---- */
  const form = document.getElementById('enquiry-form');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.textContent = 'Enquiry sent. We\'ll be in touch within 24 hours.';
      btn.disabled = true;
      btn.style.opacity = '0.75';
      form.querySelectorAll('input, textarea').forEach(f => f.disabled = true);
    });
  }

})();