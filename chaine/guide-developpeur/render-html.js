'use strict';
// Rendu HTML du guide développeur — reconstruit après perte des sources d'origine.
const fs = require('fs');
const D = __dirname;
const SRC = process.env.CONTENT || 'contenu.json';
const OUT = process.env.OUTNAME || 'guide';
const { META, SECTIONS } = JSON.parse(fs.readFileSync(D + '/' + SRC, 'utf8'));

const esc = t => String(t == null ? '' : t)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// `code`, **gras**, *italique* — appliqué après échappement
function inline(t) {
  let s = esc(t);
  s = s.replace(/`([^`]+)`/g, (m, x) => `<code>${x}</code>`);
  s = s.replace(/\*\*([^*]+)\*\*/g, (m, x) => `<strong>${x}</strong>`);
  s = s.replace(/\*([^*]+)\*/g, (m, x) => `<em>${x}</em>`);
  s = s.replace(/\n/g, '<br>');
  return s;
}

const slug = t => 'h-' + esc(t).toLowerCase()
  .normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/<[^>]+>/g, '').replace(/[^a-z0-9]+/g, '-')
  .replace(/^-|-$/g, '').slice(0, 44);

function bloc(b) {
  switch (b.t) {
    case 'lede':  return `<p class="lede">${inline(b.v)}</p>`;
    case 'p':     return `<p>${inline(b.v)}</p>`;
    case 'h2':    return `<h3 id="${slug(b.v)}">${inline(b.v)}</h3>`;
    case 'h3x':   return `<h4 class="sub" id="${slug(b.v)}">${inline(b.v)}</h4>`;
    case 'ul':    return `<ul>${b.items.map(i => `<li>${inline(i)}</li>`).join('')}</ul>`;
    case 'ol':    return `<ol class="body">${b.items.map(i => `<li>${inline(i)}</li>`).join('')}</ol>`;
    case 'note': {
      const cl = b.kind === 'info' ? 'note' : `note ${b.kind}`;
      return `<div class="${cl}"><span class="lbl">${inline(b.label)}</span>` +
             b.paras.map(p => `<p>${inline(p)}</p>`).join('') + `</div>`;
    }
    case 'fiche':
      return `<div class="fiche"><h4>${inline(b.titre)}</h4>` +
             (b.sous ? `<p class="trig">${inline(b.sous)}</p>` : '') +
             `<dl>` + b.pairs.map(([k, v]) => `<dt>${inline(k)}</dt><dd>${inline(v)}</dd>`).join('') +
             `</dl></div>`;
    case 'code':
      return `<div class="code">` +
             (b.cap ? `<div class="cap"><b>${inline(b.cap)}</b></div>` : '') +
             `<pre><code>${b.lignes.map(esc).join('\n')}</code></pre></div>`;
    case 'table': {
      const th = b.head.map(h => `<th>${inline(h)}</th>`).join('');
      const tr = b.rows.map(r => `<tr>${r.map(c => `<td>${inline(c)}</td>`).join('')}</tr>`).join('');
      return `<div class="tw"><table><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
    }
    default: return '';
  }
}

const style  = fs.readFileSync(D + '/style.css', 'utf8');
const logoG  = fs.readFileSync(D + '/logo_ghsc.txt', 'utf8').trim();
const logoU  = fs.readFileSync(D + '/logo_usa.txt', 'utf8').trim();

const toc = SECTIONS.map(s => {
  const subs = s.blocks.filter(b => b.t === 'h2');
  return `<li><a href="#s${s.num}"><span class="n">${s.num}</span><span>${esc(s.court || s.titre)}</span></a>` +
    (subs.length ? `<ul class="sub">${subs.map(x => `<li><a href="#${slug(x.v)}">${esc(x.v)}</a></li>`).join('')}</ul>` : '') +
    `</li>`;
}).join('\n    ');

const main = SECTIONS.map(s =>
  `<section id="s${s.num}">\n  <span class="sec-num">${s.num}</span>\n  <h2>${inline(s.titre)}</h2>\n` +
  s.blocks.map(bloc).join('\n') + `\n</section>`).join('\n\n');

const html = `<title>${esc(META.titre)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Carlito:wght@400;700&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">

<style>
${style}
</style>

<header class="mast">
  <div class="wrap">
    <div class="mast-inner">
      <img class="logo-ghsc" src="${logoG}" alt="U.S. Government Global Health Supply Chain Program — Procurement and Supply Management">
      <div class="kicker">
        ${META.kicker.map((k, i) => `<span>${esc(k)}</span>`).join('<span class="sep"></span>\n        ')}
      </div>
      <h1>${esc(META.titre)}</h1>
      <p class="standfirst">${esc(META.standfirst)}</p>
      <div class="mast-meta">
        ${META.chiffres.map(([k, v]) => `<span><b>${esc(k)}</b> · ${esc(v)}</span>`).join('\n        ')}
      </div>
    </div>
  </div>
</header>

<div class="wrap">
<div class="layout">

<nav class="toc">
  <p class="toc-title">Sommaire</p>
  <ol>
    ${toc}
  </ol>
</nav>

<main>

${main}

</main>
</div>
</div>

<footer>
<div class="wrap">
  <div class="foot-top">
    <div class="foot-id">
      <p class="prog">PCDD — Plan de Contrôle de Distribution des Districts</p>
      <p class="dev">${esc(META.dev)}</p>
    </div>
    <img class="logo-usa" src="${logoU}" alt="United States of America">
  </div>
  <p><em>${esc(META.colophon)}</em></p>
  <p class="foot-legal">${esc(META.legal)}</p>
</div>
</footer>
`;
fs.writeFileSync(D + '/dist/' + OUT + '.html', html);
console.log('HTML :', Math.round(html.length / 1024) + ' Ko,', SECTIONS.length, 'sections');
