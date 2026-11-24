'use strict';
// Rendu Word du guide développeur — reconstruit d'après la charte GHSC-PSM.
const fs = require('fs');
const D = __dirname;
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, AlignmentType, ImageRun, Header, Footer, PageNumber, PageBreak
} = require('docx');

const SRC = process.env.CONTENT || 'contenu.json';
const OUT = process.env.OUTNAME || 'guide';
const { META, SECTIONS } = JSON.parse(fs.readFileSync(D + '/' + SRC, 'utf8'));

/* ---------------- charte ---------------- */
const BLEU = '002F6C', BLEUC = '0067B9', BLEUP = 'E4EFF9',
      ROUGE = 'BA0C2F', ROUGEP = 'FAE5E9',
      ORANGE = 'C8701A', ORANGEP = 'FBF0E3',
      CALC = 'F0F0ED', FIL = 'CFCDC9', FILL = 'E6E4E0',
      GRIS = '6C6463', ENCRE = '1C1B1A', ENCRE2 = '403D3C', NOTEBG = 'F7FAFD';
const FT = 'Gill Sans MT', FB = 'Calibri', FM = 'Consolas';
const W = 9360;                       // largeur utile, en twips

const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const filet = c => ({ style: BorderStyle.SINGLE, size: 4, color: c });

/* ---------------- texte en ligne ---------------- */
function runs(t, base = {}) {
  const out = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  const push = (s, x = {}) => {
    if (!s) return;
    s.split('\n').forEach((part, i) => {
      if (i) out.push(new TextRun({ break: 1 }));
      out.push(new TextRun({ text: part, font: FB, size: 21, color: ENCRE2, ...base, ...x }));
    });
  };
  while ((m = re.exec(t)) !== null) {
    if (m.index > last) push(t.slice(last, m.index));
    const v = m[0];
    if (v.startsWith('`'))        push(v.slice(1, -1), { font: FM, size: 19, color: BLEUC });
    else if (v.startsWith('**'))  push(v.slice(2, -2), { bold: true, color: ENCRE });
    else                          push(v.slice(1, -1), { italics: true });
    last = re.lastIndex;
  }
  if (last < t.length) push(t.slice(last));
  return out.length ? out : [new TextRun({ text: '', font: FB, size: 21 })];
}

const par = (t, o = {}) => new Paragraph({
  children: typeof t === 'string' ? runs(t, o.run) : t,
  spacing: { before: o.before || 0, after: o.after == null ? 130 : o.after, line: o.line || 265 },
  alignment: o.align, indent: o.ind ? { left: o.ind } : undefined,
  bullet: o.puce ? { level: 0 } : undefined,
  numbering: o.num ? { reference: 'liste', level: 0 } : undefined,
});

const cell = (kids, o = {}) => new TableCell({
  children: kids, width: { size: o.w, type: WidthType.DXA },
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  borders: o.borders || { top: NONE, bottom: filet(FILL), left: NONE, right: NONE },
  margins: o.margins || { top: 90, bottom: 90, left: 130, right: 130 },
  columnSpan: o.span,
});

const tbl = (rows, widths) => new Table({
  rows, width: { size: W, type: WidthType.DXA }, columnWidths: widths,
  borders: {
    top: filet(FIL), bottom: filet(FIL), left: filet(FIL), right: filet(FIL),
    insideHorizontal: filet(FILL), insideVertical: filet(FILL),
  },
});

const spacer = (after = 170) => new Paragraph({ children: [new TextRun({ text: '', size: 10 })], spacing: { after } });

/* ---------------- blocs ---------------- */
const ACC = { info: BLEUC, warn: ORANGE, stop: ROUGE };
const BG  = { info: NOTEBG, warn: ORANGEP, stop: ROUGEP };

function bloc(b) {
  switch (b.t) {

    case 'lede':
      return [par(b.v, { run: { size: 23, color: ENCRE2 }, after: 180, line: 290 })];

    case 'p':
      return [par(b.v, { after: 140 })];

    case 'h2':
      return [par([new TextRun({ text: b.v, font: FT, size: 25, bold: true, color: BLEU })],
                  { before: 240, after: 110 })];

    case 'h3x':
      return [par([new TextRun({ text: b.v, font: FT, size: 21, bold: true, color: ENCRE })],
                  { before: 180, after: 90 })];

    case 'ul':
      return b.items.map((i, k) => par(i, { puce: true, after: k === b.items.length - 1 ? 150 : 60 }));

    case 'ol':
      return b.items.map((i, k) => par(`${k + 1}.  ${i}`, { ind: 200, after: k === b.items.length - 1 ? 150 : 60 }));

    case 'note': {
      const acc = ACC[b.kind] || BLEUC, bg = BG[b.kind] || NOTEBG;
      const kids = [par([new TextRun({ text: b.label.toUpperCase(), font: FT, size: 16,
                                       bold: true, color: acc, characterSpacing: 24 })], { after: 90 })];
      b.paras.forEach((p, i) => kids.push(par(p, { after: i === b.paras.length - 1 ? 0 : 110 })));
      return [tbl([new TableRow({ children: [cell(kids, {
        w: W, fill: bg,
        borders: { top: NONE, bottom: NONE, right: NONE,
                   left: { style: BorderStyle.SINGLE, size: 18, color: acc } },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
      })] })], [W]), spacer()];
    }

    case 'fiche': {
      const kids = [par([new TextRun({ text: b.titre, font: FT, size: 23, bold: true, color: ENCRE })],
                        { after: b.sous ? 40 : 110 })];
      if (b.sous) kids.push(par([new TextRun({ text: b.sous, font: FB, size: 19, color: ROUGE })], { after: 110 }));
      b.pairs.forEach(([k, v], i) => {
        kids.push(new Paragraph({
          children: [new TextRun({ text: k + '   ', font: FT, size: 19, bold: true, color: BLEU }),
                     ...runs(v, { size: 20 })],
          spacing: { after: i === b.pairs.length - 1 ? 0 : 70, line: 250 },
        }));
      });
      return [tbl([new TableRow({ children: [cell(kids, {
        w: W,
        borders: { top: filet(FIL), bottom: filet(FIL), left: filet(FIL), right: filet(FIL) },
        margins: { top: 150, bottom: 150, left: 180, right: 180 },
      })] })], [W]), spacer()];
    }

    case 'code': {
      const kids = [];
      if (b.cap) kids.push(par([new TextRun({ text: b.cap, font: FT, size: 17, bold: true,
                                              color: GRIS, characterSpacing: 16 })], { after: 90 }));
      b.lignes.forEach((l, i) => kids.push(new Paragraph({
        children: [new TextRun({ text: l || ' ', font: FM, size: 17, color: ENCRE2 })],
        spacing: { after: i === b.lignes.length - 1 ? 0 : 20, line: 240 },
      })));
      return [tbl([new TableRow({ children: [cell(kids, {
        w: W, fill: 'F7F7F5',
        borders: { top: filet(FIL), bottom: filet(FIL), right: filet(FIL),
                   left: { style: BorderStyle.SINGLE, size: 18, color: BLEUP } },
        margins: { top: 140, bottom: 140, left: 180, right: 180 },
      })] })], [W]), spacer()];
    }

    case 'table': {
      const n = b.head.length;
      // largeurs proportionnelles à la longueur du contenu, bornées
      const poids = b.head.map((h, i) => {
        const l = Math.max(h.length, ...b.rows.map(r => (r[i] || '').length / 2.2));
        return Math.min(Math.max(l, 8), 46);
      });
      const tot = poids.reduce((a, c) => a + c, 0);
      const ws = poids.map(p => Math.floor(W * p / tot));
      ws[n - 1] = W - ws.slice(0, n - 1).reduce((a, c) => a + c, 0);
      const head = new TableRow({
        tableHeader: true,
        children: b.head.map((h, i) => cell(
          [par([new TextRun({ text: h, font: FT, size: 15, bold: true, color: GRIS, characterSpacing: 20 })], { after: 0 })],
          { w: ws[i], fill: 'F2F2F0' })),
      });
      const rows = b.rows.map(r => new TableRow({
        children: ws.map((w, i) => cell([par(r[i] || '', { after: 0, run: { size: 18 }, line: 240 })], { w })),
      }));
      return [tbl([head, ...rows], ws), spacer()];
    }

    default: return [];
  }
}

/* ---------------- assemblage ---------------- */
const img = (f, w, h) => new Paragraph({
  children: [new ImageRun({ data: fs.readFileSync(D + '/' + f), transformation: { width: w, height: h } })],
  spacing: { after: 0 },
});

const body = [];
const add = x => body.push(x);

// page de titre
add(img('logo_ghsc.png', 252, 18));
add(new Paragraph({ children: [new TextRun({ text: META.kicker.join('   ·   '), font: FT, size: 15,
                                             color: GRIS, characterSpacing: 24 })],
                    spacing: { before: 420, after: 60 } }));
add(new Paragraph({ children: [new TextRun({ text: META.titre, font: FT, size: 60, bold: true, color: ROUGE })],
                    spacing: { after: 140, line: 720 } }));
add(par([new TextRun({ text: META.standfirst, font: FB, size: 24, color: ENCRE2 })], { after: 260 }));
add(tbl([new TableRow({ children: META.chiffres.map(([k, v]) => cell([
    par([new TextRun({ text: k.toUpperCase(), font: FT, size: 14, bold: true, color: GRIS, characterSpacing: 20 })], { after: 40 }),
    par([new TextRun({ text: v, font: FT, size: 22, bold: true, color: BLEU })], { after: 0 }),
  ], { w: Math.floor(W / META.chiffres.length), fill: CALC,
       borders: { top: NONE, bottom: NONE, left: NONE, right: NONE } })) })],
  META.chiffres.map(() => Math.floor(W / META.chiffres.length))));
add(new Paragraph({ children: [new PageBreak()] }));

// sommaire
add(new Paragraph({ children: [new TextRun({ text: 'SOMMAIRE', font: FT, size: 17, bold: true,
                                             color: GRIS, characterSpacing: 28 })], spacing: { after: 180 } }));
SECTIONS.forEach(s => {
  add(new Paragraph({
    children: [new TextRun({ text: s.num + '     ', font: FM, size: 18, color: BLEUC }),
               new TextRun({ text: s.titre, font: FT, size: 22, color: ENCRE })],
    spacing: { after: 70 }, indent: { left: 200 },
  }));
  s.blocks.filter(b => b.t === 'h2').forEach(h => add(new Paragraph({
    children: [new TextRun({ text: h.v, font: FB, size: 19, color: GRIS })],
    spacing: { after: 40 }, indent: { left: 620 },
  })));
});
add(new Paragraph({ children: [new PageBreak()] }));

// corps
SECTIONS.forEach((s, i) => {
  if (i) add(new Paragraph({ children: [new PageBreak()] }));
  add(new Paragraph({ children: [new TextRun({ text: s.num, font: FM, size: 20, bold: true, color: BLEUC })],
                      spacing: { after: 30 } }));
  add(new Paragraph({ children: [new TextRun({ text: s.titre, font: FT, size: 34, bold: true, color: ROUGE })],
                      spacing: { after: 200, line: 400 } }));
  s.blocks.forEach(b => bloc(b).forEach(add));
});

// colophon
add(new Paragraph({ children: [new TextRun({ text: '', size: 10 })], spacing: { before: 300 } }));
add(par([new TextRun({ text: META.colophon, font: FB, size: 18, italics: true, color: GRIS })], { after: 120 }));
add(par([new TextRun({ text: META.legal, font: FB, size: 16, color: GRIS })], { after: 0, line: 230 }));

const doc = new Document({
  creator: 'Chemonics International — GHSC-PSM',
  title: META.titre,
  description: 'Documentation technique de l’application Excel de contrôle des intrants antipaludiques',
  numbering: { config: [{ reference: 'liste', levels: [{ level: 0, format: 'decimal', text: '%1.', alignment: AlignmentType.START }] }] },
  styles: { default: { document: { run: { font: FB, size: 21, color: ENCRE2 },
                                   paragraph: { spacing: { after: 130, line: 265 } } } } },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 },
              margin: { top: 1440, right: 1440, bottom: 1440, left: 1440, header: 720, footer: 560 } },
      titlePage: true,
    },
    headers: {
      first: new Header({ children: [new Paragraph({ text: '' })] }),
      default: new Header({ children: [new Paragraph({
        children: [new TextRun({ text: 'PCDD — Guide développeur', font: FT, size: 15, color: GRIS, characterSpacing: 20 })],
        border: { bottom: { style: 'single', size: 6, color: ROUGE, space: 6 } }, spacing: { after: 200 },
      })] }),
    },
    footers: {
      first: new Footer({ children: [new Paragraph({ text: '' })] }),
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: 'GHSC-PSM Niger  ·  ', font: FT, size: 15, color: GRIS }),
                   new TextRun({ children: [PageNumber.CURRENT], font: FT, size: 15, color: BLEU, bold: true })],
      })] }),
    },
    children: body,
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(D + '/dist/' + OUT + '.docx', b);
  console.log('DOCX :', Math.round(b.length / 1024) + ' Ko,', SECTIONS.length, 'sections');
});
