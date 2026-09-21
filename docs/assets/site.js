'use strict';
const figures = {
  2: ['Nine-field atomic node schema, four relation types, and the two-unit occupancy rule.', 'Figure 2 · Nine node fields, typed relations, and execution-unit occupancy.'],
  3: ['Four local repair transformations followed by a joint audit and a strict schedule; the B task spans both units.', 'Figure 3 · Local repair transformations and scheduling after audit. Resource and compression panels are local examples.'],
  4: ['Accepted-event replay, six graph audits, accepted outputs and failure diagnostics, and the guarantee boundary.', 'Figure 4 · Replayable edits, six joint checks, accepted artifacts, and failure diagnostics.']
};
document.querySelectorAll('[data-figure]').forEach(button => {
  button.addEventListener('click', () => {
    const id = button.dataset.figure;
    const image = document.getElementById('method-image');
    image.src = `assets/images/figure${id}.png`;
    image.alt = figures[id][0];
    document.getElementById('method-full').href = image.src;
    document.getElementById('method-caption').textContent = figures[id][1] + ' Click the image for full resolution.';
    document.querySelectorAll('[data-figure]').forEach(other => {
      const selected = other === button;
      other.classList.toggle('active', selected);
      other.setAttribute('aria-pressed', String(selected));
    });
  });
});
document.getElementById('copy-command').addEventListener('click', async () => {
  const status = document.getElementById('copy-status');
  try {
    await navigator.clipboard.writeText(document.getElementById('run-command').textContent);
    status.textContent = 'Command copied. Run it from the extracted supplementary archive root.';
  } catch {
    status.textContent = 'Select and copy the command above. Clipboard access is unavailable in this browser.';
  }
});
if (!['localhost', '127.0.0.1', ''].includes(location.hostname)) {
  document.getElementById('local-note').hidden = true;
}
