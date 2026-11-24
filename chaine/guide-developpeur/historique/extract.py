"""Relit le guide HTML produit par l'ancienne chaîne et en reconstitue le contenu
   sous forme de données. Le HTML ayant été produit par le générateur lui-même,
   son balisage est régulier et la relecture est fidèle."""
import re, json, html as H

s = open('/home/claude/gen/source.html', encoding='utf8').read()
body = s[s.index('<main>') + 6 : s.index('</main>')]

def inline(t):
    """HTML en ligne -> notation du contenu (`code`, **gras**, *italique*)."""
    t = re.sub(r'<code>(.*?)</code>', lambda m: '`' + m.group(1) + '`', t, flags=re.S)
    t = re.sub(r'<strong>(.*?)</strong>', lambda m: '**' + m.group(1) + '**', t, flags=re.S)
    t = re.sub(r'<em>(.*?)</em>', lambda m: '*' + m.group(1) + '*', t, flags=re.S)
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    return H.unescape(t).strip()

def cells(row, tag):
    return [inline(c) for c in re.findall(r'<%s[^>]*>(.*?)</%s>' % (tag, tag), row, re.S)]

SECTIONS = []
for sm in re.finditer(r'<section id="s(\d+)">(.*?)</section>', body, re.S):
    num, inner = sm.group(1), sm.group(2)
    titre = inline(re.search(r'<h2>(.*?)</h2>', inner, re.S).group(1))
    inner = inner[inner.index('</h2>') + 5:]
    blocks = []
    pos = 0
    # on parcourt les blocs de premier niveau dans l'ordre
    pat = re.compile(
        r'<div class="note( warn| stop)?">(?P<note>.*?)</div>\s*(?=<|$)'
        r'|<div class="fiche">(?P<fiche>.*?)</div>\s*(?=<|$)'
        r'|<div class="code">(?P<code>.*?)</pre>\s*</div>'
        r'|<div class="tw">(?P<tw>.*?)</table>\s*</div>'
        r'|<h3[^>]*>(?P<h3>.*?)</h3>'
        r'|<p class="lede">(?P<lede>.*?)</p>'
        r'|<ol class="body">(?P<ol>.*?)</ol>'
        r'|<ul>(?P<ul>.*?)</ul>'
        r'|<p>(?P<p>.*?)</p>', re.S)
    for m in pat.finditer(inner):
        g = m.groupdict()
        if g['note'] is not None:
            kind = {' warn': 'warn', ' stop': 'stop'}.get(m.group(1) or '', 'info')
            n = g['note']
            lbl = re.search(r'<span class="lbl">(.*?)</span>', n, re.S)
            paras = [inline(x) for x in re.findall(r'<p>(.*?)</p>', n, re.S)]
            blocks.append({'t': 'note', 'kind': kind,
                           'label': inline(lbl.group(1)) if lbl else '', 'paras': paras})
        elif g['fiche'] is not None:
            f = g['fiche']
            h4 = re.search(r'<h4>(.*?)</h4>', f, re.S)
            tr = re.search(r'<p class="trig">(.*?)</p>', f, re.S)
            dt = [inline(x) for x in re.findall(r'<dt>(.*?)</dt>', f, re.S)]
            dd = [inline(x) for x in re.findall(r'<dd>(.*?)</dd>', f, re.S)]
            blocks.append({'t': 'fiche', 'titre': inline(h4.group(1)) if h4 else '',
                           'sous': inline(tr.group(1)) if tr else '',
                           'pairs': [list(x) for x in zip(dt, dd)]})
        elif g['code'] is not None:
            c = g['code']
            cap = re.search(r'<div class="cap">(.*?)</div>', c, re.S)
            pre = re.search(r'<pre><code>(.*)', c, re.S)
            lignes = H.unescape(re.sub(r'<[^>]+>', '', pre.group(1))).split('\n') if pre else []
            blocks.append({'t': 'code', 'cap': inline(cap.group(1)) if cap else '',
                           'lignes': lignes})
        elif g['tw'] is not None:
            tb = g['tw']
            head = cells(re.search(r'<thead>(.*?)</thead>', tb, re.S).group(1), 'th')
            rows = [cells(r, 'td') for r in re.findall(r'<tr[^>]*>(.*?)</tr>',
                    re.search(r'<tbody>(.*?)$', tb, re.S).group(1), re.S)]
            rows = [r for r in rows if r]
            blocks.append({'t': 'table', 'head': head, 'rows': rows})
        elif g['h3'] is not None:
            blocks.append({'t': 'h2', 'v': inline(g['h3'])})
        elif g['lede'] is not None:
            blocks.append({'t': 'lede', 'v': inline(g['lede'])})
        elif g['ol'] is not None:
            blocks.append({'t': 'ol', 'items': [inline(x) for x in
                           re.findall(r'<li>(.*?)</li>', g['ol'], re.S)]})
        elif g['ul'] is not None:
            blocks.append({'t': 'ul', 'items': [inline(x) for x in
                           re.findall(r'<li>(.*?)</li>', g['ul'], re.S)]})
        elif g['p'] is not None:
            txt = inline(g['p'])
            if txt:
                blocks.append({'t': 'p', 'v': txt})
    SECTIONS.append({'num': num, 'titre': titre, 'blocks': blocks})

# métadonnées depuis l'en-tête
mast = s[s.index('<header class="mast">'):s.index('</header>')]
META = {
    'titre': inline(re.search(r'<h1>(.*?)</h1>', mast, re.S).group(1)),
    'standfirst': inline(re.search(r'<p class="standfirst">(.*?)</p>', mast, re.S).group(1)),
    'kicker': [inline(x) for x in re.findall(r'<span>(.*?)</span>', mast, re.S)][:3],
    'chiffres': [[inline(a), inline(b)] for a, b in
                 re.findall(r'<span><b>(.*?)</b> · (.*?)</span>', mast, re.S)],
}
pied = s[s.index('<footer>'):]
META['dev'] = inline(re.search(r'<p class="dev">(.*?)</p>', pied, re.S).group(1))
META['colophon'] = inline(re.findall(r'<p>(.*?)</p>', pied, re.S)[-1])
META['legal'] = inline(re.search(r'<p class="foot-legal">(.*?)</p>', pied, re.S).group(1))

json.dump({'META': META, 'SECTIONS': SECTIONS},
          open('/home/claude/gen/contenu.json', 'w', encoding='utf8'),
          ensure_ascii=False, indent=1)

n = sum(len(x['blocks']) for x in SECTIONS)
print(f"{len(SECTIONS)} sections, {n} blocs")
from collections import Counter
print(Counter(b['t'] for x in SECTIONS for b in x['blocks']))
