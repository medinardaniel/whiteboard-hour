// ArrowRight reveals the next hidden step on the current slide, or moves to the next slide.
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  let i = 0;
  slides[0].classList.add('active');
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowRight') return;
    const next = slides[i].querySelector('.step:not(.on)');
    if (next) { next.classList.add('on'); return; }
    if (i < slides.length - 1) {
      slides[i].classList.remove('active');
      i += 1;
      slides[i].classList.add('active');
    }
  });
})();
