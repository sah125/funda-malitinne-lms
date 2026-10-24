/* Funda Malitinne staff portal: small, dependency-free behaviours. */
(function () {
  'use strict';

  function cookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }

  // ---- sidebar on small screens
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-nav-toggle]')) { document.body.classList.toggle('nav-open'); }
    else if (e.target.classList.contains('scrim')) { document.body.classList.remove('nav-open'); }
  });

  // ---- whole table row clickable (links inside still work normally)
  document.addEventListener('click', function (e) {
    var row = e.target.closest('tr[data-href]');
    if (!row || e.target.closest('a,button,input,select,form')) return;
    window.location = row.getAttribute('data-href');
  });

  // ---- dialogs: <button data-open="id"> / <button data-close>
  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[data-open]');
    if (opener) {
      var dlg = document.getElementById(opener.getAttribute('data-open'));
      if (!dlg) return;
      e.preventDefault();
      // prefill fields from data-set-<name> attributes (e.g. upload a new version of a vault document)
      Array.prototype.forEach.call(opener.attributes, function (a) {
        if (a.name.indexOf('data-set-') !== 0) return;
        var field = dlg.querySelector('[name="' + a.name.slice(9) + '"]');
        if (field) field.value = a.value;
      });
      var title = opener.getAttribute('data-title');
      if (title && dlg.querySelector('[data-dialog-title]')) dlg.querySelector('[data-dialog-title]').textContent = title;
      var src = opener.getAttribute('data-src');
      if (src) {
        var frame = dlg.querySelector('iframe, img');
        if (frame) frame.src = src;
        var dl = dlg.querySelector('[data-download]');
        if (dl) dl.href = src.replace('?inline=1', '');
        var nt = dlg.querySelector('[data-newtab]');
        if (nt) nt.href = src;
      }
      dlg.showModal();
    }
    if (e.target.closest('[data-close]')) {
      var d = e.target.closest('dialog');
      if (d) { d.close(); var f = d.querySelector('iframe'); if (f) f.src = 'about:blank'; }
    }
  });
  document.querySelectorAll('dialog[data-autoshow]').forEach(function (d) { d.showModal(); });

  // ---- drag & drop upload
  document.querySelectorAll('[data-dropzone]').forEach(function (zone) {
    var input = zone.querySelector('input[type=file]');
    var label = zone.querySelector('[data-file-label]');
    var form = zone.closest('form');
    function show() {
      if (input.files.length && label) label.textContent = input.files[0].name + ' (' + Math.round(input.files[0].size / 1024) + ' KB)';
      var title = form && form.querySelector('[name=title]');
      if (title && !title.value && input.files.length) title.value = input.files[0].name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');
    }
    ['dragenter', 'dragover'].forEach(function (t) { zone.addEventListener(t, function (e) { e.preventDefault(); zone.classList.add('over'); }); });
    ['dragleave', 'drop'].forEach(function (t) { zone.addEventListener(t, function (e) { e.preventDefault(); zone.classList.remove('over'); }); });
    zone.addEventListener('drop', function (e) { if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; show(); } });
    input.addEventListener('change', show);
  });

  // ---- confirm destructive actions
  document.addEventListener('submit', function (e) {
    var msg = e.target.getAttribute('data-confirm');
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  // ---- copy buttons
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy]');
    if (!b) return;
    var input = document.getElementById(b.getAttribute('data-copy'));
    if (!input) return;
    input.select();
    (navigator.clipboard ? navigator.clipboard.writeText(input.value) : Promise.resolve(document.execCommand('copy')))
      .then(function () { var t = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = t; }, 1500); });
  });

  // ---- operations assistant (answers rendered as text, never as HTML)
  var box = document.querySelector('[data-assistant]');
  if (box) {
    var form = box.querySelector('form'), input = box.querySelector('input'), out = box.querySelector('.answer');
    function render(data) {
      out.textContent = '';
      if (data.error) { out.appendChild(el('p', { class: 'state-expired' }, data.error)); return; }
      if (data.message) out.appendChild(el('p', {}, data.message.split('\n')[0]));
      var rows = data.projects || data.learners || data.tickets || data.urgent_actions || [];
      if (data.suggestions) rows = data.suggestions.map(function (s) { return { name: s }; });
      if (rows.length) {
        var ul = el('ul');
        rows.slice(0, 10).forEach(function (r) {
          var text = r.name || r.title || r.username || r.description || '';
          var extra = [];
          if (r.attendance != null) extra.push('attendance ' + r.attendance + '%');
          if (r.learners != null) extra.push(r.learners + ' learners');
          if (r.email) extra.push(r.email);
          if (r.project__title) extra.push(r.project__title);
          if (r.count != null) extra.push(r.count);
          ul.appendChild(el('li', {}, text + (extra.length ? ' (' + extra.join(', ') + ')' : '')));
        });
        out.appendChild(ul);
      }
      if (data.type === 'compliance') {
        var c = el('ul');
        [['POPIA consent', data.popia_consent], ['Attendance compliance', data.attendance_compliance], ['POE compliance', data.poe_compliance]]
          .forEach(function (p) { c.appendChild(el('li', {}, p[0] + ': ' + p[1])); });
        out.appendChild(c);
      }
    }
    function ask(q) {
      out.textContent = 'Working on it...';
      fetch(box.getAttribute('data-assistant'), {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cookie('csrftoken') },
        body: JSON.stringify({ query: q })
      }).then(function (r) { return r.json(); }).then(render)
        .catch(function () { render({ error: 'The assistant is not reachable right now. Try again in a moment.' }); });
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); if (input.value.trim()) ask(input.value.trim()); });
    box.querySelectorAll('.chips button').forEach(function (b) {
      b.addEventListener('click', function () { input.value = b.textContent; ask(b.textContent); });
    });
  }
})();
