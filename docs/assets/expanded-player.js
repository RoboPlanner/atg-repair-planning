(() => {
  'use strict';
  const root = document.getElementById('simulation-player');
  const data = window.ATG_EXPANDED;
  if (!root || !data) return;
  const video = document.getElementById('simulation-video');
  const task = document.getElementById('simulation-task');
  const condition = document.getElementById('simulation-condition');
  const play = document.getElementById('simulation-play');
  let mode = 'full';
  function playState() { play.textContent = video.paused ? 'Play video' : 'Pause video'; }
  function choose() {
    const resume = !video.paused;
    video.pause();
    if (task.value !== 'T08') condition.value = 'nominal';
    condition.disabled = task.value !== 'T08';
    if (condition.value !== 'nominal') mode = 'full';
    const c = data.cases.find(x => x.task === task.value);
    const r = data.videos.find(x => x.task === task.value && x.condition === condition.value && x.mode === mode);
    const outcome = data.per_task.find(x => x.task === task.value && x.condition === condition.value);
    video.src = r.src; video.poster = r.poster;
    video.setAttribute('aria-label', `${c.title}, ${r.condition}, ${mode}, actual MuJoCo simulation`);
    video.load();
    document.getElementById('simulation-title').textContent = `${c.task} · ${c.title}`;
    document.getElementById('simulation-subtitle').textContent = `Seed 100, selected before evaluation · ${r.success ? 'Completed' : 'Execution failed; retained in results'}`;
    document.getElementById('simulation-times').textContent = `${c.serial_window_s} → ${c.full_window_s} s`;
    document.getElementById('simulation-success').textContent = `${outcome.success} / ${outcome.n}`;
    document.getElementById('simulation-record').textContent = r.success ? 'Completed' : 'Failed';
    document.getElementById('simulation-record').dataset.outcome = r.success ? 'pass' : 'fail';
    document.getElementById('simulation-download').href = r.src;
    document.getElementById('simulation-description').textContent = data.descriptions[c.task];
    document.getElementById('simulation-failure').textContent = r.success ? 'The selected recording meets the declared execution checks.' : `Observed checks: ${r.failures.join('; ')}. Remaining actions are stopped; failure is not hidden.`;
    root.querySelectorAll('[data-sim-mode]').forEach(el => {
      el.disabled = condition.value !== 'nominal' && el.dataset.simMode === 'serial';
      el.setAttribute('aria-pressed', String(el.dataset.simMode === mode));
    });
    playState();
    if (resume) video.play().catch(playState);
  }
  task.addEventListener('change', choose); condition.addEventListener('change', choose);
  root.querySelectorAll('[data-sim-mode]').forEach(el => el.addEventListener('click', () => { mode = el.dataset.simMode; choose(); }));
  play.addEventListener('click', () => { if(video.paused) video.play().catch(playState); else video.pause(); });
  video.addEventListener('play', playState); video.addEventListener('pause', playState);
  video.addEventListener('loadedmetadata', () => { video.playbackRate = Number(document.getElementById('simulation-speed').value); });
  document.getElementById('simulation-speed').addEventListener('change', e => { video.playbackRate = Number(e.target.value); });
  choose();
})();
