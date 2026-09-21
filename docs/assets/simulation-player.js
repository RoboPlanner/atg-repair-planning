(() => {
  'use strict';
  const root = document.getElementById('simulation-player');
  if (!root || !window.ATG_SIMULATION) return;
  const data = window.ATG_SIMULATION;
  const video = document.getElementById('simulation-video');
  const play = document.getElementById('simulation-play');
  let index = 0;
  let mode = 'full';
  const updateButton = () => {
    play.textContent = video.paused ? 'Play video' : 'Pause video';
  };
  function choose() {
    const wasPlaying = !video.paused;
    video.pause();
    const c = data.cases[index];
    video.src = `assets/videos/${c.case}_${mode}.mp4`;
    video.poster = `assets/videos/${c.case}_${mode}.png`;
    video.setAttribute('aria-label', `${c.title}, ${mode === 'full' ? 'full method' : 'serial control'}, actual MuJoCo recording`);
    video.load();
    document.getElementById('simulation-title').textContent = c.title;
    document.getElementById('simulation-subtitle').textContent = 'Seed 0, fixed before evaluation · 5 paired initial positions per scene';
    document.getElementById('simulation-times').textContent = `${c.serial.makespan_s} → ${c.full.makespan_s} s`;
    document.getElementById('simulation-success').textContent = `${c.full.successes}/${c.full.n} · ${c.serial.successes}/${c.serial.n}`;
    document.getElementById('simulation-error').textContent = `${c.full.max_goal_error_mm.toFixed(1)} mm`;
    document.getElementById('simulation-download').href = video.getAttribute('src');
    document.getElementById('simulation-description').textContent = [
      'Both arms grasp and place separate objects in parallel. The serial control uses the same repaired graph, object targets, assignments, and fixed skill windows.',
      'Both arms share one geometric service station. Resource ordering serializes the service operations while allowing other eligible actions to overlap.',
      'Both grippers make frictional contact with the tray and move it together. The B task reserves L + R simultaneously; approach and retreat can run in parallel.'
    ][index];
    root.querySelectorAll('[data-sim-case]').forEach((el, i) => el.setAttribute('aria-pressed', String(i === index)));
    root.querySelectorAll('[data-sim-mode]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.simMode === mode)));
    updateButton();
    if (wasPlaying) video.play().catch(updateButton);
  }
  root.querySelectorAll('[data-sim-case]').forEach((el,i) => el.addEventListener('click', () => {index=i;choose();}));
  root.querySelectorAll('[data-sim-mode]').forEach(el => el.addEventListener('click', () => {mode=el.dataset.simMode;choose();}));
  play.addEventListener('click', () => {if (video.paused) video.play().catch(updateButton);else video.pause();});
  video.addEventListener('play', updateButton);
  video.addEventListener('pause', updateButton);
  video.addEventListener('loadedmetadata', () => {video.playbackRate=Number(document.getElementById('simulation-speed').value);});
  document.getElementById('simulation-speed').addEventListener('change', e => {video.playbackRate=Number(e.target.value);});
  choose();
})();
