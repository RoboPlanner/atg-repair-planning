(() => {
  'use strict';
  const clips = [...document.querySelectorAll('.teaser-video')];
  const toggle = document.getElementById('teaser-toggle');
  if (!toggle) return;
  let enabled = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const visible = new Set();
  function update() {
    clips.forEach(video => {
      if (enabled && visible.has(video) && !document.hidden) video.play().catch(() => {});
      else video.pause();
    });
    toggle.textContent = enabled ? 'Pause previews' : 'Play previews';
    toggle.setAttribute('aria-pressed', String(!enabled));
  }
  clips.forEach(video => { video.muted = true; video.removeAttribute('autoplay'); });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target));
    update();
  }, {threshold: 0.15});
  clips.forEach(video => observer.observe(video));
  toggle.addEventListener('click', () => { enabled = !enabled; update(); });
  document.addEventListener('visibilitychange', update);
  document.querySelectorAll('[data-preview-task]').forEach(link => {
    link.addEventListener('click', () => {
      const task = document.getElementById('simulation-task');
      task.value = link.dataset.previewTask;
      document.getElementById('simulation-condition').value = 'nominal';
      document.querySelector('[data-sim-mode="full"]').click();
      task.dispatchEvent(new Event('change', {bubbles: true}));
    });
  });
  update();
})();
