/* TEMPLATE: copy this folder to start a series, then replace everything. Labels here are layout
   placeholders, not researched content. One object per page; pages play in order. */
window.SERIES = { runhead: '2026 Working Note on [Topic]' };
window.PAGES = [];
(function () {
  var W = window.WorkingPaper;
  function P(o) { window.PAGES.push(o); }

  P({
    folio: 1,
    runR: 'October 2026',                       /* page 1: month and year; later pages: 'Part n of N' */
    title: 'Topic in one line<br>and the claim',  /* page 1 uses title; later pages use heading: '...' */
    dek: 'One sentence, two lines, naming the tension the figure resolves',
    caption: '<b>Fig. 1.</b> What the figure shows and what to watch. Sources: Name (Mon 2026).',
    runin: 'Abstract.',
    body: '45 to 70 words, readable at about four words a second. Italicise a term of art on first use, cite sources by name and month, and mark invented numbers as illustrative.',
    tall: false,                                /* true: figure starts at 330px and is 680px tall */
    build: function (s) {                       /* figure canvas is 904 x 626 (680 when tall) */
      W.panel(s, { x: 92, y: 0, w: 700, h: 470 });
      W.actor(s, { id: 'u', x: 40, y: 200, label: 'The user', sub: 'asks', lx: 0 });
      W.node(s, { id: 'app', x: 130, y: 170, w: 180, h: 60, label: 'App', sub: 'builds the prompt' });
      W.node(s, { id: 'hub', kind: 'hub', x: 380, y: 166, w: 220, h: 68, label: 'Retriever', sub: ['embed', 'search', 'rank'] });
      W.group(s, { id: 'gI', x: 360, y: 300, w: 260, h: 130, label: 'Index', labelAlign: 'start' });
      W.node(s, { id: 'v1', kind: 'chip', dot: true, x: 376, y: 326, w: 110, h: 40, label: 'Chunks' });
      W.node(s, { id: 'v2', kind: 'chip', dot: true, x: 494, y: 326, w: 110, h: 40, label: 'Vectors' });
      W.node(s, { id: 'm', x: 640, y: 40, w: 136, h: 60, label: 'Model', sub: 'answers' });
      W.line(s, { id: 'e-u', pts: [[60, 200], [130, 200]] });
      W.line(s, { id: 'e-q', pts: [[310, 200], [380, 200]] });
      W.line(s, { id: 'e-s', pts: [[490, 234], [490, 300]] });
      W.line(s, { id: 'e-r', quiet: true, pts: [[540, 300], [540, 234]] });
      W.line(s, { id: 'e-m', pts: [[220, 170], [220, 70], [640, 70]], label: { text: 'question + passages', x: 430, y: 60 } });
      W.line(s, { id: 'l-seam', noArrow: true, pts: [[442, 470], [442, 500]] });
      W.pill(s, { id: 'pill', cx: 442, cy: 522, w: 260, label: 'TOPIC · STACK' });
    },
    spec: {
      story: [                                  /* 4-7 steps; each step is one beat */
        { pulse: '#e-u', then: '#e-q', light: '#app', light2: '#hub', shimmer: '#pill' },
        { pulse: '#e-s', hub: '#hub', verbs: [1], hubNow: true, flash: '#gI' },
        { pulse: '#e-r', hub: '#hub', verbs: [2], hub1: true },
        { pulse: '#e-m', light: '#m' }
      ]
    }
  });
})();
