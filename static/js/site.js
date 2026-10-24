/* Malitinne public site behaviour */
(function () {
    var navbar = document.getElementById('navbar');
    if (navbar && !navbar.classList.contains('scrolled-fixed')) {
        var initial = navbar.classList.contains('scrolled');
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('scrolled', initial || window.scrollY > 60);
        }, { passive: true });
    }

    window.openMobileMenu = function () { var m = document.getElementById('mobileMenu'); m.classList.add('open'); m.setAttribute('aria-hidden', 'false'); };
    window.closeMobileMenu = function () { var m = document.getElementById('mobileMenu'); m.classList.remove('open'); m.setAttribute('aria-hidden', 'true'); };
    document.querySelectorAll('#mobileMenu a').forEach(function (a) { a.addEventListener('click', window.closeMobileMenu); });

    var fades = document.querySelectorAll('.fade-in');
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry, i) {
                if (entry.isIntersecting) { setTimeout(function () { entry.target.classList.add('visible'); }, i * 80); observer.unobserve(entry.target); }
            });
        }, { threshold: 0.1 });
        fades.forEach(function (el) { observer.observe(el); });
    } else {
        fades.forEach(function (el) { el.classList.add('visible'); });
    }

    function animateCounters() {
        document.querySelectorAll('.impact-number, .stat-number, [data-count]').forEach(function (el) {
            var target = el.textContent;
            var num = parseFloat(target.replace(/[^0-9.]/g, ''));
            if (!num) return;
            var suffix = target.replace(/[0-9.,\s]/g, '');
            var current = 0, step = num / 50;
            var timer = setInterval(function () {
                current = Math.min(current + step, num);
                el.textContent = Math.floor(current).toLocaleString('en-ZA') + suffix;
                if (current >= num) clearInterval(timer);
            }, 25);
        });
    }
    var counterTargets = document.querySelectorAll('.impact-grid, .stats-grid, .trust-row');
    if (counterTargets.length && 'IntersectionObserver' in window) {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) { if (e.isIntersecting) { animateCounters(); co.disconnect(); } });
        }, { threshold: 0.3 });
        counterTargets.forEach(function (el) { co.observe(el); });
    }

    // Auto-hide flash messages
    setTimeout(function () {
        document.querySelectorAll('.flash.success, .flash.info').forEach(function (f) { f.style.transition = 'opacity .5s'; f.style.opacity = '0'; setTimeout(function () { f.remove(); }, 600); });
    }, 7000);
})();

/* ---- Service map (Leaflet) ---- */
window.initServiceMap = function (points, opts) {
    opts = opts || {};
    var el = document.getElementById(opts.el || 'serviceMap');
    if (!el || typeof L === 'undefined') return;
    var map = L.map(el, { scrollWheelZoom: false }).setView([-28.9, 30.9], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18, attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    var markers = [];
    var bounds = [];
    points.forEach(function (p, i) {
        var icon = L.divIcon({ className: '', html: '<div class="map-pin ' + p.kind + '"></div>', iconSize: [24, 24], iconAnchor: [12, 12] });
        var list = (p.programmes || []).map(function (x) { return '<li>' + escapeHtml(x) + '</li>'; }).join('');
        var html = '<h4>' + escapeHtml(p.name) + '</h4>' +
            '<div style="color:#888">' + escapeHtml([p.town, p.province].filter(Boolean).join(', ')) + (p.period ? ' · ' + escapeHtml(p.period) : '') + '</div>' +
            (p.beneficiaries ? '<div style="margin-top:6px"><strong style="color:#7a5828">' + Number(p.beneficiaries).toLocaleString('en-ZA') + '</strong> beneficiaries</div>' : '') +
            (list ? '<ul>' + list + '</ul>' : '');
        var m = L.marker([p.lat, p.lng], { icon: icon, title: p.name }).addTo(map).bindPopup(html);
        markers.push(m);
        bounds.push([p.lat, p.lng]);
    });
    if (bounds.length > 1) map.fitBounds(bounds, { padding: [30, 30] });
    document.querySelectorAll('[data-map-index]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var m = markers[+btn.getAttribute('data-map-index')];
            if (!m) return;
            document.querySelectorAll('[data-map-index]').forEach(function (b) { b.classList.remove('on'); });
            btn.classList.add('on');
            map.flyTo(m.getLatLng(), 10, { duration: 0.8 });
            setTimeout(function () { m.openPopup(); }, 850);
        });
    });
    el.addEventListener('click', function () { map.scrollWheelZoom.enable(); });
    return map;
};

function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
}

// ===== Gallery: category filters + lightbox =====
(function () {
    document.querySelectorAll('.gallery-filters').forEach(function (bar) {
        var grid = bar.parentElement.querySelector('[data-gallery]');
        bar.addEventListener('click', function (e) {
            var btn = e.target.closest('button[data-filter]');
            if (!btn || !grid) return;
            bar.querySelectorAll('button').forEach(function (b) { b.classList.toggle('active', b === btn); });
            var f = btn.getAttribute('data-filter');
            grid.querySelectorAll('.gallery-item').forEach(function (item) {
                item.hidden = !(f === 'all' || item.getAttribute('data-category') === f);
            });
        });
    });

    var openers = function () { return Array.prototype.filter.call(document.querySelectorAll('.gallery-open'), function (b) { return !b.closest('[hidden]'); }); };
    if (!document.querySelector('.gallery-open')) return;
    var box = document.createElement('div');
    box.className = 'lightbox'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Photo viewer');
    box.innerHTML = '<button type="button" class="lb-close" aria-label="Close">&times;</button><button type="button" class="lb-prev" aria-label="Previous photo">&#8249;</button><img alt=""><p></p><button type="button" class="lb-next" aria-label="Next photo">&#8250;</button>';
    document.body.appendChild(box);
    var img = box.querySelector('img'), cap = box.querySelector('p'), current = 0, lastFocus = null;
    function show(i) {
        var list = openers(); if (!list.length) return;
        current = (i + list.length) % list.length;
        img.src = list[current].getAttribute('data-full');
        img.alt = cap.textContent = list[current].getAttribute('data-caption') || '';
    }
    function close() { box.classList.remove('open'); document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.gallery-open');
        if (!btn) return;
        lastFocus = btn; show(openers().indexOf(btn));
        box.classList.add('open'); document.body.style.overflow = 'hidden'; box.querySelector('.lb-close').focus();
    });
    box.addEventListener('click', function (e) {
        if (e.target === box || e.target.classList.contains('lb-close')) close();
        else if (e.target.classList.contains('lb-prev')) show(current - 1);
        else if (e.target.classList.contains('lb-next')) show(current + 1);
    });
    document.addEventListener('keydown', function (e) {
        if (!box.classList.contains('open')) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft') show(current - 1);
        else if (e.key === 'ArrowRight') show(current + 1);
    });
})();
