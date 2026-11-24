"""Mise à jour du guide sur les classeurs finaux — novembre 2026.

Le guide avait été établi sur PCDD.xlsm et sur la copie d'Illéla. Les versions
finales livrées par Boubacar Garba — PCDD_Ok.xlsm et
Module_Visualisation_FINAL_OK.xlsm — ajoutent des procédures et modifient le
contenu du Module6 du PCDD. Par ailleurs, la réorganisation en six parties avait
laissé des renvois aux anciennes sections 05 à 11, qui n'existent plus.

Relevés sur les classeurs finaux :
  PCDD_Ok.xlsm                      23 feuilles · 7 tableaux · 1 requête PQ
                                    13 TCD (5 sur le cache Power Query)
                                    19 procédures VBA
  Module_Visualisation_FINAL_OK.xlsm 14 feuilles · 5 tableaux
                                    20 procédures VBA
"""
import json, re

P = '/home/claude/PCDD/chaine/guide-developpeur/contenu.json'
d = json.load(open(P, encoding='utf8'))

# ---------------------------------------------------------------- colophon
d['META']['colophon'] = (
    '*Document établi sur les classeurs de référence `PCDD_Ok.xlsm` et '
    '`Module_Visualisation_FINAL_OK.xlsm`, dans leur version de novembre 2026. '
    'Les exemples de configuration — chemins, noms de fichiers, volumes de '
    'données — sont pris sur la copie du district d’Illéla ; toute autre '
    'installation s’obtient en substituant le compte de l’officier et le nom du '
    'district. Formules transcrites en notation française ; les noms de '
    'cellules, de plages et de procédures sont ceux du code.*')

d['META']['kicker'] = ['Niger',
                       'PCDD — PLAN DE CONTRÔLE DE DISTRIBUTION DES DISTRICTS',
                       'Novembre 2026']
d['META']['dev'] = ('Développé par Chemonics International dans le cadre du projet '
                    'GHSC-PSM.\nDéveloppeur : Boubacar Garba. Niger  ·  Novembre 2026.')
d['META']['chiffres'] = [['Parties', '6'], ['Classeurs', '3'],
                         ['Procédures VBA', '39'], ['Contrôles recensés', '12']]

# ------------------------------------------------- substitutions textuelles
SUBS = [
    # renvois laissés par la réorganisation en six parties
    ('les chemins recensés au § 02', 'les chemins recensés au § 01'),
    ('la checklist du § 02', 'la checklist du § 01'),
    ('décrite au § 02', 'décrite au § 01'),
    ('Ré-encoder les chemins recensés au § 01, sans en sauter un.',
     'Ré-encoder les chemins recensés au § 01, sans en sauter un.'),
    ('voir § 05', 'voir § 04'),
    ('§ 06 niveau 2', '§ 03 niveau 2'),
    ('§ 06 niveau 3', '§ 03 niveau 3'),
    ('Voir le § 09.', 'Voir le § 04, chapitre « Étape 2-B ».'),
    ('contient un bloc inactif (§ 07)',
     'contient un bloc inactif (§ 04, chapitre « Étape 1 »)'),
    ('les variables non déclarées recensées au § 11.',
     'les variables non déclarées recensées au début de cette partie.'),
    # comptages relevés sur les classeurs finaux
    ('une requête Power Query, dix-sept procédures VBA',
     'une requête Power Query, dix-neuf procédures VBA'),
    ('Dix-sept procédures dans le PCDD, dix-neuf dans le Module de Visualisation.',
     'Dix-neuf procédures dans le PCDD, vingt dans le Module de Visualisation.'),
]

def fix(s):
    for a, b in SUBS:
        s = s.replace(a, b)
    return s

def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v) for v in o]
    if isinstance(o, str):
        return fix(o)
    return o

d['SECTIONS'] = walk(d['SECTIONS'])

# ------------------------------------- table de correspondance étape ↔ partie
S = d['SECTIONS']
for b in S[0]['blocks']:
    if b['t'] == 'table' and b['head'][:1] == ['Étape (guide d’utilisation)']:
        b['head'][1] = 'Partie de ce guide'
        b['rows'][0][1] = '§ 04, chapitre « Étape 1 »'
        b['rows'][1][1] = ('§ 04, chapitres « Étape 2-A » — paramétrage et arbitrage — '
                           'et « Étape 2-B » — rapport et validation MCD')
        b['rows'][2][1] = '§ 04, chapitre « Étape 3 »'

# --------------------------------- Module6 du PCDD : nouveau contenu, v. finale
n = 0
for s in S:
    for b in s['blocks']:
        if b['t'] == 'table' and 'Déclencheur' in b['head']:
            for r in b['rows']:
                if r[0] == '`Module6`' and 'macro' in r[1]:
                    r[1] = '`Supprimer_Lignes_Apres_Total_General`'
                    r[3] = ('Nettoie la feuille `Rapport_CMD_PDF` : supprime les dix '
                            'lignes qui suivent la mention « Total général ». Ajoutée '
                            'dans la version finale, câblée à aucun bouton — elle se '
                            'lance depuis l’éditeur VBA.')
                    n += 1

json.dump(d, open(P, 'w', encoding='utf8'), ensure_ascii=False, indent=1)

txt = json.dumps(d, ensure_ascii=False)
print('Module6 corrigé :', n)
print('renvois § restants :', sorted(set(re.findall(r'§ ?(\d{1,2})', txt))))
for p in ['Illela', 'dix-sept', 'PCDD_Ok', 'FINAL_OK',
          'Supprimer_Lignes_Apres_Total_General']:
    print(f'  {p:38s} {len(re.findall(re.escape(p), txt))}')
