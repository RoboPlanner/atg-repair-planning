/* Playback of immutable archived schedules; this file never plans or reschedules. */
(() => {
  'use strict';
  const root = document.getElementById('experiment-player');
  if (!root || !window.ATG_REPLAYS) return;
  const cases = window.ATG_REPLAYS.cases;
  const $ = id => document.getElementById(id);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let selected = 0;
  let playing = !reduced.matches;
  let visible = false;
  let phase = 0;
  let previous = 0;
  let speed = 1;
  let progressBars = [];
  let graphNodes = [];
  let clockLines = [];
  let cards = [];
  let lastStatus = '';
  const fmt = n => Number(n.toFixed(2)).toString();
  const stateAt = (item, time) => time < item.start ? 'waiting' : time < item.finish ? 'running' : 'complete';
  const setButton = () => {
    $('replay-play').textContent = playing ? 'Pause' : 'Play';
    $('replay-play').setAttribute('aria-label', playing ? 'Pause experiment animation' : 'Play experiment animation');
  };

  function render(time) {
    const c = cases[selected];
    const k = 924 / c.horizon;
    $('replay-time').textContent = `${fmt(time)} / ${fmt(c.horizon)}`;
    $('replay-seek').value = String(time / c.horizon * 1000);
    $('replay-seek').setAttribute('aria-valuetext', `${fmt(time)} of ${fmt(c.horizon)} symbolic time units`);
    clockLines.forEach(line => {
      line.setAttribute('x1', String(68 + time * k));
      line.setAttribute('x2', String(68 + time * k));
    });
    progressBars.forEach(({element, item}) => {
      const elapsed = Math.max(0, Math.min(time, item.finish) - item.start);
      element.setAttribute('width', String(elapsed * k));
    });
    graphNodes.forEach(({element, item}) => {
      const state = stateAt(item, time);
      element.setAttribute('fill-opacity', state === 'running' ? '.75' : state === 'complete' ? '.4' : '.12');
      element.setAttribute('stroke-width', state === 'running' ? '3' : '1.5');
    });
    const status = [];
    cards.forEach(({element, plan, unit}) => {
      const item = plan.schedule.items.find(s => stateAt(s, time) === 'running' && s.executors.includes(unit));
      const complete = time >= plan.schedule.estimated_makespan;
      const mode = item?.executors.length === 2 ? 'both' : unit;
      element.dataset.occupancy = item ? mode : 'idle';
      const text = item ? `${item.node_id} · ${item.action} ${item.object}` : complete ? 'All tasks complete' : 'Idle';
      const resource = item ? (item.executors.length === 2 ? 'B: L + R together · ' : '') + (item.resources.length ? item.resources.join(', ') : 'No resource declared') : '—';
      element.querySelector('.live-task').textContent = text;
      element.querySelector('.live-resource').textContent = resource;
      status.push(text);
    });
    const signature = status.join('|');
    if (signature !== lastStatus) {
      $('replay-summary').textContent = c.plans.map(p => `${p.label}: ${p.schedule.items.filter(s => s.finish <= time).length}/${p.schedule.items.length} tasks complete`).join(' · ');
      lastStatus = signature;
    }
  }

  function choose(index) {
    selected = index;
    phase = 0;
    previous = 0;
    lastStatus = '';
    const c = cases[index];
    $('replay-title').textContent = c.title;
    $('replay-subtitle').textContent = c.subtitle;
    $('replay-note').textContent = c.note;
    $('replay-svg').innerHTML = c.svg;
    $('replay-download').href = `assets/animations/${c.id}.svg`;
    $('replay-download').download = `${c.id}.svg`;
    $('replay-source').textContent = `Record ${c.record_id} · v7.70 archive`;
    root.querySelectorAll('[data-replay-case]').forEach((button, i) => {
      button.classList.toggle('active', i === index);
      button.setAttribute('aria-pressed', String(i === index));
    });
    progressBars = [...root.querySelectorAll('[data-progress]')].map(element => ({
      element,
      item: c.plans[Number(element.dataset.plan)].schedule.items.find(x => x.node_id === element.dataset.progress)
    }));
    graphNodes = [...root.querySelectorAll('[data-node]')].map(element => ({
      element,
      item: c.plans[0].schedule.items.find(x => x.node_id === element.dataset.node)
    }));
    clockLines = [...root.querySelectorAll('[data-clock]')];
    const holder = $('replay-units');
    holder.replaceChildren();
    cards = [];
    c.plans.forEach(plan => {
      const group = document.createElement('div');
      group.className = 'live-plan';
      const title = document.createElement('p');
      title.className = 'live-plan-title';
      title.textContent = plan.label;
      group.append(title);
      ['left', 'right'].forEach((unit, i) => {
        const element = document.createElement('div');
        element.className = 'live-unit';
        element.innerHTML = `<strong class="live-letter">${i === 0 ? 'L' : 'R'}</strong><div><p class="live-task"></p><p class="live-resource"></p></div>`;
        group.append(element);
        cards.push({element, plan, unit});
      });
      holder.append(group);
    });
    render(0);
    setButton();
  }

  root.querySelectorAll('[data-replay-case]').forEach((button, i) => button.addEventListener('click', () => choose(i)));
  $('replay-play').addEventListener('click', () => { playing = !playing; previous = 0; setButton(); });
  $('replay-restart').addEventListener('click', () => { phase = 0; previous = 0; render(0); });
  $('replay-seek').addEventListener('input', event => {
    playing = false;
    phase = Number(event.target.value) / 1000 * 12;
    previous = 0;
    setButton();
    render(cases[selected].horizon * Math.min(phase / 12, 1));
  });
  $('replay-speed').addEventListener('change', event => { speed = Number(event.target.value); previous = 0; });
  reduced.addEventListener('change', event => { if (event.matches) { playing = false; setButton(); } });
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; previous = 0; }, {threshold: 0.12}).observe(root);
  document.addEventListener('visibilitychange', () => { previous = 0; });
  function tick(timestamp) {
    if (playing && visible && !document.hidden) {
      if (previous) phase = (phase + Math.min((timestamp - previous) / 1000, 0.15) * speed) % 14;
      previous = timestamp;
      render(cases[selected].horizon * Math.min(phase / 12, 1));
    } else previous = 0;
    requestAnimationFrame(tick);
  }
  choose(0);
  requestAnimationFrame(tick);
})();
