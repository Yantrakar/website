/* Yantrakar site script: theme toggle + animated figures. Vanilla JS. */
(() => {
	const d = document, root = d.documentElement;
	const tb = d.querySelector('.theme-toggle');
	if (tb) {
		/* system = no data-theme (the device decides; dark when it says nothing). Each click: system, then the opposite of the device, then the device, then system again. */
		const mq = matchMedia('(prefers-color-scheme: light)');
		const cur = () => root.getAttribute('data-theme') || 'system';
		const dev = () => mq.matches ? 'light' : 'dark';
		const next = v => v === 'system' ? (dev() === 'dark' ? 'light' : 'dark') : v === dev() ? 'system' : dev();
		const label = v => tb.querySelector('[data-icon="' + v + '"] .sr-only').textContent;
		const mark = v => { tb.dataset.current = v; tb.title = label(v); };
		const st = d.createElement('span');
		st.className = 'sr-only'; st.setAttribute('role', 'status'); tb.after(st);
		mark(cur()); tb.hidden = false;
		tb.onclick = () => {
			const v = next(cur());
			if (v === 'system') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', v);
			try { if (v === 'system') localStorage.removeItem('yk-theme'); else localStorage.setItem('yk-theme', v); } catch (e) { }
			mark(v); st.textContent = label(v);
		};
	}
	if (matchMedia('(prefers-reduced-motion: reduce)').matches || !window.IntersectionObserver) return;
	const SPD = [0.18, 0.5, 1.5], BLD = {}, figs = [];
	let raf = 0, last = 0;
	const at = (e, a) => { for (const k in a) e.setAttribute(k, a[k]); return e; };
	const mk = (n, a, p) => (p || { appendChild: e => e }).appendChild(at(d.createElementNS('http://www.w3.org/2000/svg', n), a));
	function G(S, k) {
		const e = S.q(k), a = n => +e.getAttribute(n);
		if (e.tagName == 'line') return { x: a('x1'), y: a('y1'), y2: a('y2') };
		if (e.tagName == 'g') return { x: +e.firstChild.getAttribute('x1') };
		const x = a('x'), y = a('y'), w = a('width'), h = a('height');
		return { x, y, w, cx: x + w / 2, cy: y + h / 2, r: x + w, b: y + h };
	}
	const txt = (S, k, x, y, cls, anchor) => { S.c[k] = mk('text', { class: cls, x, y, 'text-anchor': anchor || 'start', 'data-k': k }, S.u); };
	function TL(S) {
		const T = { ev: [], tw: [], end: 0 };
		T.at = (t, f) => { T.ev.push([t, f]); if (t > T.end) T.end = t; };
		T.cl = (t, k, c, on) => T.at(t, () => { const e = S.q(k); if (e) e.classList.toggle(c, on); });
		T.hit = (t, k) => T.cl(t, k, k == 'x-mark' ? 'flash' : 'hit', 1);
		T.act = (t, k, ms) => { T.cl(t, k, 'active', 1); T.cl(t + ms, k, 'active', 0); };
		T.tx = (t, k, s) => T.at(t, () => { const e = S.q(k); if (e) e.textContent = s; });
		T.pk = (t, pts, o = {}) => {
			let segs = [], p = pts[0], s0 = t;
			let u = o.m ? S.mkr : S.pool.find(c => c.until <= t);
			if (!u) { u = { el: mk('circle', {}, S.g) }; if (o.m) S.mkr = u; else S.pool.push(u); }
			pts.forEach((q, i) => {
				if (!i) return;
				const dx = q[0] - p[0], dy = q[1] - p[1];
				segs.push({ x: p[0], y: p[1], dx, dy, d: Math.hypot(dx, dy) / SPD[q[3] || 0], h: q[3] == 2 });
				p = q;
				if (q[2] || i == pts.length - 1) {
					const sum = segs.reduce((s, g) => s + g.d, 0), D = Math.max(sum, 260);
					segs.forEach(g => { g.d = sum ? g.d * D / sum : 0; });
					T.tw.push({ el: u.el, s: s0, d: D, segs, keep: o.m || i < pts.length - 1, cl: o.m ? 'mk' : 'pkt' + (o.a ? ' a' : ''), r: o.m ? 7 : o.r || 4 });
					s0 += D; segs = [];
					if (q[2]) T.hit(s0, q[2]);
				}
			});
			u.until = s0; if (s0 > T.end) T.end = s0;
			return s0;
		};
		return T;
	}
	function place(w, t) {
		let e = t - w.s, i = 0, k;
		if (e < 0 || w.fin) return;
		if (e > w.d) { w.fin = 1; e = w.d; }
		if (!w.on) at(w.el, { class: w.cl, r: w.r });
		w.on = 1; k = (e = e / w.d) * e * (3 - 2 * e) * w.d;
		for (; i < w.segs.length - 1 && k > w.segs[i].d; i++) k -= w.segs[i].d;
		const s = w.segs[i], g = s.d ? k / s.d : 1;
		at(w.el, { cx: (s.x + s.dx * g).toFixed(1), cy: (s.y + s.dy * g).toFixed(1) });
		w.el.style.transitionDuration = s.h ? '0s' : '';
		w.el.style.opacity = s.h || (w.fin && !w.keep) ? 0 : 1;
	}
	function run(S, t) {
		const tl = S.tl;
		while (S.i < tl.ev.length && tl.ev[S.i][0] <= t) tl.ev[S.i++][1]();
		tl.tw.forEach(w => place(w, t));
	}
	function reset(S) {
		S.svg.querySelectorAll('.hit,.active,.flash,.on').forEach(e => e.classList.remove('hit', 'active', 'flash', 'on'));
		S.i = 0;
		S.pool.forEach(p => { p.until = 0; });
		const T = TL(S);
		S.build(S, T, S.n, k => G(S, k));
		T.ev.sort((a, b) => a[0] - b[0]); S.tl = T;
	}
	BLD.f00 = (S, T, n, g) => {
		const W = S.svg.dataset.v == 'w', bo = g('band-ops'), bi = g('band-int'), bm = g('band-mach'), fr = g('frame'),
			st = g('c-state'), ta = g('c-task'), lm = g('c-models'), cm = g('c-common'), cr = g('c-ctrl'), sp = g('stop'),
			yo = bo.b - 11.5, yi = bi.b - 11.5, lx = bo.x + 7, x = g('ar12-0-up').x, xd = g(W ? 'ar01-1-dn' : 'ar01-0-dn').x;
		if (!S.c.st) txt(S, 'st', fr.r - 16, W ? 34 : 54, 'st', 'end');
		T.tx(0, 'st', 'STATE UP'); T.hit(0, 'c-robots');
		/* state up: machines to integration to operations */
		const t2 = T.pk(250, [[x, bm.y], [x, bi.b, 'band-int'], [x, yi], [x, cm.cy, 'c-common', 2], [x, bi.y, 0, 2], [x, bo.b], [x, yo], [lx, yo], [lx, st.cy, 'c-state']]) + 350;
		/* command down: operations to integration to machines */
		T.tx(t2, 'st', 'COMMAND DOWN'); T.act(t2, 'c-task', 700);
		const t3 = T.pk(t2, [[ta.cx, ta.b + 4], [ta.cx, yo], [xd, yo], [xd, bi.y, 'band-int'],
			...(W ? [[xd, cm.cy], [cm.r + 4, cm.cy, 'c-common'], [xd, cm.cy], [xd, bm.y + 18], [cr.cx, bm.y + 18], [cr.cx, cr.y - 5, 'c-ctrl']]
				: [[xd, cm.cy, 'c-common', 2], [xd, bi.b, 0, 2], [xd, bm.y], [xd, cr.cy, 'c-ctrl', 2]])]) + 450;
		/* private AI stands apart: its local models try to send out and are blocked at the boundary */
		T.tx(t3, 'st', 'SEND OUTSIDE?'); T.act(t3, 'c-models', 800);
		T.pk(t3 + 800, [[sp.x, lm.b + 3], [sp.x, sp.y, 'x-mark'], [sp.x, sp.y]], { a: 1 });
	};
	BLD.f01 = (S, T, n, g) => {
		const N = S.svg.dataset.v == 'n', ex = g('bd-ex'), bi = g('bd-int'), bo = g('bd-ops'), tk = g('i-task'), co = g('i-coll'), pt = g('i-proto'),
			pr = N ? [['i-robots', 'i-ctrl'], ['i-ctrl', 'i-robots']][n % 2] : [['i-robots', 'i-plcs'], ['i-drones', 'i-ctrl'], ['i-svc', 'i-robots']][n % 3],
			s = g(pr[0]), dst = g(pr[1]), cm = g('i-common'), uu = g('ar-ie-up').x, ud = g('ar-ie-dn').x, ou = g('ar-oi-up').x, od = g('ar-oi-dn').x,
			yI = bi.b - 6, yO = bo.b - 6, strip = ex.y + 5.5;
		if (!S.c.st) txt(S, 'st', S.svg.viewBox.baseVal.width - 4, 16, 'st', 'end');
		T.tx(0, 'st', 'READING STATE'); T.hit(0, pr[0]);
		if (N) {
			/* narrow: packets ride the lane left of the chips; each chip lights as the packet passes its row */
			const sc = g('i-state'), row = k => g(k).cy;
			const t = T.pk(250, [[uu, s.cy], [uu, ex.y, 'bd-ex'], [uu, bi.b, 'bd-int'], [uu, row('i-proto')], [uu, row('i-coll'), 'i-coll'], [uu, row('i-common'), 'i-common'],
				[uu, bi.y], [ou, bo.b], [ou, sc.cy, 'i-state']]) + 500;
			T.tx(t, 'st', 'SENDING A COMMAND'); T.act(t, 'i-task', 600);
			T.pk(t, [[od, tk.cy], [od, bo.b], [od, bi.y, 'bd-int'], [od, row('i-common'), 'i-common'], [od, row('i-proto'), 'i-proto'], [od, bi.b], [ud, ex.y, 'bd-ex'], [ud, dst.cy, pr[1]]]);
			return;
		}
		const t = T.pk(250, [[s.cx, strip], [uu, strip, 0, 1], [uu, bi.b, 'bd-int'], [uu, yI], [co.x + 24, yI, 'i-coll', 1],
			[uu, yI, 'i-common', 1], [uu, bi.y + 5.5, 0, 2], [ou, yO, 'i-state']]) + 500;
		T.tx(t, 'st', 'SENDING A COMMAND'); T.act(t, 'i-task', 600);
		T.pk(t, [[tk.cx, yO], [od, yO], [od, bi.y, 'bd-int'], [od, cm.cy, 'i-common', 2], [od, yI, 0, 2],
			[pt.cx, yI, 'i-proto', 1], [ud, yI, 0, 2], [ud, ex.y], [ud, strip], [dst.cx, strip, 0, 1],
			[dst.cx, dst.y - 4, pr[1], dst.x < 30 ? 2 : 0]]);
	};
	BLD.f02 = (S, T, n, g) => {
		const b = g('band'), y = b.b - 8, w = [75, 105, 67], R = [...'abc'];
		if (!S.c.zn) {
			const N = S.svg.dataset.v == 'n', ws = N ? [72, 101, 65] : w, gp = (b.w - ws[0] - ws[1] - ws[2]) / 4;
			['zn', 'pt', 'sp'].forEach((k, j) => txt(S, k, (N ? b.x + gp * (j + 1) + ws.slice(0, j).reduce((a, c) => a + c, 0) : b.x + b.w * (2 * j + 1) / 6 - w[j] / 2).toFixed(1), y, 'lbl-mono stf'));
			for (let i = 0; i < 3; i++) { const q = S.q('q' + (i + 1)); S.c['ck' + i] = mk('path', { class: 'ck', d: 'M' + (q.getAttribute('x') - 17) + ' ' + (q.getAttribute('y') - 5) + 'l3 4l6-10' }, S.u); }
		}
		const fld = (t, z, p, s) => { if (z) T.tx(t, 'zn', 'ZONE: ' + z); if (p) T.tx(t, 'pt', 'PART: ' + p); if (s) T.tx(t, 'sp', 'STEP: ' + s); };
		fld(0, 'FREE', 'WAITING', '0/3');
		R.forEach(r => { T.tx(0, 'role-' + r, 'waiting'); T.tx(0, 'role2-' + r, ''); });
		const done = [['FREE', 'IN PLACE', '1/3'], ['FREE', 0, '2/3'], ['FREE', 'JOINED', '3/3']];
		let t = 300;
		R.forEach((r, j) => {
			const rd = g('rd-' + r), pb = g('pub-' + r), rl = 'role-' + r,
				pub = t0 => T.pk(t0, [[pb.x, pb.y + 4], [pb.x, pb.y2 - 3, 'band']]);
			T.tx(t, rl, 'checking');
			for (let i = 0; i < 3; i++) { T.cl(t, 'q' + (i + 1), 'on', 0); T.cl(t, 'ck' + i, 'on', 0); }
			let e = T.pk(t, [[rd.x, rd.y], [rd.x, rd.y2 + 4, 'rb-' + r]]);
			/* every robot asks all three questions, one after another */
			for (let i = 0; i < 3; i++) { T.cl(e + 300 * i, 'q' + (i + 1), 'on', 1); T.cl(e + 300 * i, 'ck' + i, 'on', 1); }
			e += 250; T.tx(e, rl, 'working'); T.cl(e, 'rb-' + r, 'active', 1);
			e = pub(e); fld(e, 'BUSY');
			if (j == 1) {
				const a = g('rd-plc'), c = g('pub-plc'), p = T.pk(e + 100, [[a.x, a.y + 4], [a.x, a.y2 - 4, 'plc']]);
				T.pk(p + 150, [[c.x, c.y - 4], [c.x, c.y2 + 4, 'band']]);
			}
			e += 1300; T.tx(e, rl, 'done'); T.cl(e, 'rb-' + r, 'active', 0);
			e = pub(e); fld(e, ...done[j]);
			t = e + 450;
		});
		const o = g('rd-op'); T.pk(t, [[o.x, o.y + 4], [o.x, o.y2 - 4, 'op']]);
	};
	BLD.f03 = (S, T, n, g) => {
		const N = S.svg.dataset.v == 'n', lv = g('live'), sn = g('sens');
		const runs = [['A', 'station 2', 'M', '0'], ['B', 'station 4', 'L', '3']];
		const lb = ['which item', 'where it is', 'its size', 'its offset'];
		if (!S.c.v2) {
			const s2 = g('s2'), s3 = g('s3');
			txt(S, 'v2', N ? s2.r - 12 : s2.x + 28, N ? s2.y + 25 : 52, 'sub val', N ? 'end' : 0); txt(S, 'v3', N ? s3.r - 12 : s3.x + 28, N ? s3.y + 25 : 52, 'sub val', N ? 'end' : 0);
			txt(S, 'st', N ? S.svg.viewBox.baseVal.width - 6 : g('s5').r, 14, 'st', 'end');
		}
		let t = 0;
		runs.forEach((r, j) => {
			T.tx(t, 'st', 'RUN ' + (j + 1) + ' · item ' + r[0]);
			let e = T.pk(t, [[sn.r, sn.cy], [lv.x - 4, sn.cy, 'live']]);
			lb.forEach((l, i) => T.tx(e, 'lv' + (i + 1), l + ': ' + r[i]));
			t = e + 250;
			for (let i = 1; i < 6; i++) {
				const s = g('s' + i), s0 = g('s' + Math.max(1, i - 1)), z = t + 900 * (i - 1), k = 's' + i, ln = s.x - 17;
				T.act(z, k, 900);
				T.pk(z, N ? [[ln, s0.cy], [ln, s.cy, 0, 1]] : [[s0.x + 14, s.y], [s.x + 14, s.y, 0, 1]], { m: 1 });
				if (i == 2 || i == 3) {
					const u = g('up' + i), tr = N && g('trunk');
					T.tx(T.pk(z + 100, N ? [[tr.x, lv.y - 2], [tr.x, u.y, 0, 1], [s.r + 4, u.y, k, 1]] : [[u.x, u.y - 4], [u.x, u.y2 + 4, k]], { a: 1 }), 'v' + i, i < 3 ? r[1] : 'size ' + r[2]);
				}
			}
			t += 4800;
			T.at(t - 100, () => { S.mkr.el.style.opacity = 0; });
			lb.forEach((l, i) => T.tx(t - 100, 'lv' + (i + 1), l)); T.tx(t - 100, 'v2', ''); T.tx(t - 100, 'v3', '');
		});
	};
	BLD.f05 = (S, T, n, g) => {
		const N = S.svg.dataset.v == 'n', hn = g('harness'), hx = hn.x + 8, hr = hn.r, fr = g('frame'), mx = N ? 36 : 456;
		if (!S.c.st) txt(S, 'st', N ? fr.r - 16 : 740, N ? 46 : 27, 'st', 'end');
		const cn = k => g('cn-' + k), cy = m => g('cm-' + m).y,
			out = (t, from, m, o) => T.pk(t, N ? [from, [hx, cy(m)], [mx, cy(m), 'm-' + m]] : [from, [hr, cy(m), 0, 2], [mx, cy(m), 'm-' + m]], o);
		let t = 0;
		/* label, tool, harness items visited, model, helper model */
		[['CODE QUESTION', 'code', ['router', 'access'], 'coding'], ['QUESTION ABOUT A DOCUMENT', 'docs', ['router', 'index'], 'general', 'embed'],
			['PHOTO FROM SITE', 'chat', ['router'], 'vision']].forEach(([label, tool, items, m, helper]) => {
			const c = cn(tool), last = g('it-' + items[items.length - 1]), yh = c.y2 + 11;
			T.tx(t, 'st', label); T.hit(t, 'tl-' + tool);
			let e = T.pk(t, [...(N ? [[c.x, c.y], [c.x, yh], [hx, yh]] : [[c.x, c.y], [hx, c.y]]), ...items.map(k => [hx, g('it-' + k).cy, 'it-' + k])], { a: 1 }) + 100;
			if (helper) {
				const b = out(e, [hx, last.cy], helper, { r: 3 });
				T.act(b, 'm-' + helper, 600); T.pk(b + 600, N ? [[mx, cy(helper)], [hx, cy(helper)]] : [[mx, cy(helper)], [hr, cy(helper)]], { r: 3 });
			}
			e = out(e, [hx, last.cy], m) + 700;
			T.act(e - 700, 'm-' + m, 700);
			t = T.pk(e, N ? [[mx, cy(m)], [hx, cy(m)], [hx, yh], [c.x, yh], [c.x, c.y + 4, 'tl-' + tool]] : [[mx, cy(m)], [hr, cy(m)], [hn.x, c.y, 0, 2], [c.x + 4, c.y, 'tl-' + tool]]) + 450;
		});
		T.tx(t, 'st', 'SEND OUTSIDE?'); T.hit(t, 'harness');
		if (N) { const xs = g('x-mark').x + 5; T.pk(t, [[hr - 7, hn.cy], [hr + 9, hn.cy], [hr + 9, fr.b - 6], [xs, fr.b - 6], [xs, fr.b - 1, 'x-mark'], [xs, fr.b - 1]], { a: 1 }); }
		else T.pk(t, [[hr - 8, hn.b - 15], [hr - 8, hn.b + 6.5], [fr.r - 118, hn.b + 6.5, 'x-mark'], [fr.r - 118, hn.b + 6.5]], { a: 1 });
	};
	const start = f => { f.t = f.len = 0; f.s.forEach(S => { S.n = f.n; reset(S); f.len = Math.max(f.len, S.tl.end); }); };
	const on = f => f.vis && !f.pa;
	function tick(now) {
		const dt = Math.min(now - last, 80); last = now; raf = 0;
		figs.filter(on).forEach(f => {
			f.t += dt; f.s.forEach(S => run(S, f.t));
			if (f.t > f.len + 1200) { f.n++; start(f); }
		});
		if (figs.some(on)) raf = requestAnimationFrame(tick); /* browsers pause rAF while the tab is hidden */
	}
	const wake = () => { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } };
	const io = new IntersectionObserver(es => es.forEach(x => {
		const f = x.target._f; f.vis = x.intersectionRatio > 0.34;
		if (f.vis && !f.go) { f.go = 1; start(f); }
		if (f.vis) wake();
	}), { threshold: [0, 0.35] });
	d.querySelectorAll('figure[data-anim]').forEach(el => {
		const f = { el, s: [], n: 0, vis: 0, pa: 0 };
		el.querySelectorAll('svg[data-fig]').forEach(svg => {
			const S = { svg, c: {}, build: BLD[svg.dataset.fig], pool: [], n: 0, i: 0 };
			svg.onanimationend = e => e.target.classList.remove('hit', 'flash');
			S.u = mk('g', { 'aria-hidden': 'true' }, svg); S.g = mk('g', { class: 'pkts' }, S.u);
			S.q = k => S.c[k] || (S.c[k] = svg.querySelector('[data-k="' + k + '"]'));
			if (S.build) f.s.push(S);
		});
		if (!f.s.length) return;
		el.classList.add('anim'); el._f = f;
		const b = d.createElement('button');
		b.type = 'button'; b.className = 'fig-ctl'; b.textContent = 'Pause'; b.setAttribute('aria-pressed', 'false');
		b.onclick = () => { f.pa = !f.pa; b.textContent = f.pa ? 'Play' : 'Pause'; b.setAttribute('aria-pressed', f.pa); wake(); };
		el.querySelector('.fig-head').appendChild(b);
		figs.push(f); io.observe(el);
	});
})();
