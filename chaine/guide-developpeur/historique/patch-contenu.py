"""Intègre la relecture de Boubacar Garba (17 nov. 2026), formulations reprises,
   puis réorganise le guide en six parties par composant."""
import json, copy

d = json.load(open('/home/claude/gen/contenu.json', encoding='utf8'))
S = {s['num']: s for s in d['SECTIONS']}
B = lambda n: S[n]['blocks']

note  = lambda k, l, *p: {'t': 'note', 'kind': k, 'label': l, 'paras': list(p)}
para  = lambda v: {'t': 'p', 'v': v}
h2    = lambda v: {'t': 'h2', 'v': v}
code  = lambda cap, *l: {'t': 'code', 'cap': cap, 'lignes': list(l)}

# =====================================================================
# 1. Compatibilité Excel — apport de Boubacar, rédaction reprise
# =====================================================================
B('02').insert(8, note('stop', 'Version d’Excel requise',
  'Le PCDD et le Module de Visualisation reposent sur des fonctions matricielles dynamiques '
  'qui n’existent qu’à partir de Microsoft 365 : `FILTRE`, `UNIQUE`, `TRIER`, `RECHERCHEX`, '
  '`LET` et `CHOISIRCOLS`. À elles seules, `FILTRE` et `RECHERCHEX` apparaissent plus de '
  'trois cents fois dans le classeur.',
  'Sur une version antérieure — Office 2019 ou 2016 —, le calcul n’est pas faux : il n’a pas '
  'lieu. Les cellules concernées affichent `#NOM?`, la CMMA ne se calcule plus et les boutons '
  'ne s’affichent pas. Microsoft 365 est donc un prérequis d’installation au même titre que '
  'les chemins d’accès.'))

# =====================================================================
# 2. Colonnes de complétude et de cohérence — apport de Boubacar
# =====================================================================
B('03')[5]['rows'] += [
  ['Analyse Base', 'Signale les lignes dont les quatre indicateurs se contredisent',
   'Colonne `N` — `NB`, `SI`, `OU`, `ET`, `JOUR` et `SIERREUR` sur l’export DHIS2'],
  ['Complétude', 'Complétude par CSI et par produit',
   'Colonnes `AN` et `AO` — `NB` et `SI` sur l’export DHIS2'],
  ['Complétude interprétée', 'Même calcul, mais un seul indicateur renseigné pour un produit '
   'suffit à considérer les autres comme renseignés',
   'Colonnes `AP` et `AQ` — `ET`, `SI`, `MOYENNE` et `INDIRECT`'],
  ['ID_Saisie', 'Clé unique par ligne de produit et par CSI',
   'Colonne `Y` — concaténation'],
  ['Date Opération', 'Date et heure de l’enregistrement',
   'Colonne `Z` — `SI` et `MAINTENANT`'],
  ['Test Doublons', 'Teste si l’enregistrement existe déjà dans la Base Historique',
   'Colonne `AA` — `SI`, `ESTNA` et `RECHERCHEV`'],
  ['Complétude Du', 'Rattache à chaque ligne la date de complétude saisie en `P12`',
   'Colonne `AD` — `SI`'],
]

bloc_formules = [
  h2('Les formules de contrôle et d’horodatage'),
  para('Sept colonnes de `Data_Produit_Saisie` ne portent pas de donnée logistique : elles '
       'contrôlent, identifient et horodatent. Les formules sont transcrites en notation '
       'française ; la ligne 2 sert de référence, la formule étant recopiée sur toute la colonne.'),
  code('Data_Produit_Saisie — contrôle, clé, horodatage',
   'N    =SI(NB(H2:K2)=4;',
   '        SIERREUR(SI(OU(ET(H2=0; J2=0; R2=0; K2>0);',
   '                       ET(H2=0; J2=0; K2=0; I2=0);',
   '                       ET(OU(H2>0; J2>0); K2=0; I2>0);',
   '                       K2>(H2+J2+Q2);',
   '                       ET(OU(H2>0; J2>0); I2=JOUR(M2)));',
   '                 "données incohérentes"; ""); "");',
   '        "")',
   '',
   'Y    =SI($A$3=55; B2&C2&D2&$P$12; "")',
   'Z    =SI($A$3=55; MAINTENANT(); "")',
   'AA   =SI($A$3=55;',
   '        SI(ESTNA(RECHERCHEV(B2&C2&D2&$P$12;',
   '                 Data_Produit_Historique!$X:$X; 1; FAUX)); "Ok"; "Doublons");',
   '        "")',
   'AD   =SI($P$12=""; ""; $P$12)'),
  para('La colonne `N` ne se prononce que si les quatre indicateurs sont renseignés — '
       '`NB(H2:K2)=4`. Elle signale alors une incohérence dans cinq cas : consommation '
       'déclarée sans stock ni réception ; ligne entièrement à zéro ; stock en début de mois '
       'mais aucune consommation alors que des jours de rupture sont déclarés ; consommation '
       'supérieure à tout ce qui a pu être disponible ; rupture couvrant le mois entier malgré '
       'un stock initial.'),
  note('info', 'Le verrou de saisie',
   'Les colonnes `Y`, `Z`, `AA` et `AD` ne se remplissent que si la cellule `A3` vaut 55. '
   'Tant que ce verrou n’est pas levé, aucune clé ni aucun horodatage n’est produit, ce qui '
   'interdit un transfert accidentel vers la Base Historique.',
   'La colonne `AA` interroge ensuite la Base Historique par `RECHERCHEV` sur sa colonne `X`, '
   'qui porte la même clé concaténée. C’est ce test qui produit le signal « Doublons » et '
   'bloque la sauvegarde d’une période déjà enregistrée.'),
]
B('03')[6:6] = bloc_formules

# =====================================================================
# 3. Suppressions demandées — reliquats retirés au prochain déploiement
# =====================================================================
del B('04')[11:13]                                   # colonne Type de CMMA Antérieure
B('05')[2]['rows'] = [r for r in B('05')[2]['rows'] if r and r[0].strip('`') != 'Feuil1']
for b in B('05'):                                    # la colonne disparaît aussi des TCD
    if b['t'] == 'table':
        b['rows'] = [r for r in b['rows'] if 'Type de CMMA Antérieure' not in ' '.join(r)]

# =====================================================================
# 4. Mot de passe — objet rétabli, l'ancienne note laissait entendre une faille
# =====================================================================
B('11')[5] = note('info', 'Conventions du projet',
  'Aucun module ne déclare `Option Explicit`, et plusieurs variables sont utilisées sans `Dim`. '
  'Activer `Option Explicit` sur l’ensemble du projet, puis compiler, révèle en une passe les '
  'fautes de frappe qui se traduisent aujourd’hui par des comportements silencieux.',
  'Les feuilles sont protégées par le mot de passe `Chemonics`, écrit en clair dans les '
  'procédures qui déprotègent puis reprotègent. Cette protection vise l’écrasement accidentel '
  'des formules par l’utilisateur ; elle ne restreint pas l’accès au code, qui reste ouvert à '
  'tout intervenant autorisé.')

# =====================================================================
# 5. Plage figée à 24 lignes — reformulée en consigne de maintenance
# =====================================================================
B('06')[14] = note('warn', 'Plage à étendre si un produit est ajouté',
  'La plage `CMMA!$H$8:$H$31` est dimensionnée à 24 lignes, soit 3 mois × 8 produits, et le '
  'référentiel compte aujourd’hui huit produits actifs.',
  'L’ajout d’un neuvième produit impose donc d’étendre cette plage dans le même mouvement. '
  'À défaut, des lignes sortent de la moyenne sans qu’aucun message ne le signale : la CMMA '
  'reste affichée, mais elle est calculée sur une partie seulement des données.')

# =====================================================================
# 6. Formule de la CMMA — l'encart est conservé, reformulé au présent
# =====================================================================
for i, b in enumerate(B('06')):
    if b['t'] == 'note' and 'TROIS CORRECTIONS' in b.get('label', '').upper():
        B('06')[i] = note('retenir', 'Trois conditions que la formule doit conserver', *b['paras'])
        break
else:
    B('06').insert(7, note('warn', 'Trois conditions que la formule doit conserver',
      'La moyenne filtre explicitement sur le site — `$D$3:$D$400 = D8` —, exclut les valeurs '
      'nulles et teste `ESTNUM` avant d’intégrer une ligne.',
      'Ces trois conditions ne sont pas des précautions d’écriture : chacune corrige un défaut '
      'constaté. Les retirer pour « simplifier » la formule ramènerait une CMMA calculée sur '
      'd’autres sites, minorée par les mois à zéro, ou interrompue par une valeur textuelle.'))

json.dump(d, open('/home/claude/gen/contenu.json', 'w', encoding='utf8'),
          ensure_ascii=False, indent=1)
print('relecture intégrée — %d sections, %d blocs'
      % (len(d['SECTIONS']), sum(len(s['blocks']) for s in d['SECTIONS'])))
