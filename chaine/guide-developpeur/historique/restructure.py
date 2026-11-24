"""Réorganise le guide en six parties par composant, selon la structure
   proposée par Boubacar Garba et arrêtée avec Frédérick Persoons.

   Les douze sections suivaient le flux des données ; les six parties suivent
   les fichiers. Le déroulé de la session mensuelle, qui expliquait le
   séquencement du code, est conservé comme chapitre de la partie 4."""
import json

d = json.load(open('/home/claude/gen/contenu.json', encoding='utf8'))
S = {s['num']: s for s in d['SECTIONS']}

h2   = lambda v: {'t': 'h2', 'v': v}
para = lambda v: {'t': 'p', 'v': v}
lede = lambda v: {'t': 'lede', 'v': v}
note = lambda k, l, *p: {'t': 'note', 'kind': k, 'label': l, 'paras': list(p)}

def corps(num, saut=None):
    """Blocs d'une ancienne section, le chapeau retiré ou converti."""
    bl = [b for b in S[num]['blocks']]
    if saut == 'lede':
        bl = [b for b in bl if b['t'] != 'lede']
    return bl

def titrer(num, titre):
    """Ancienne section ramenée au rang de chapitre."""
    bl = corps(num)
    out = [h2(titre)]
    for b in bl:
        if b['t'] == 'lede':
            out.append(para(b['v']))          # le chapeau devient un paragraphe
        elif b['t'] == 'h2':
            out.append({'t': 'h3x', 'v': b['v']})   # rétrogradé d'un niveau
        else:
            out.append(b)
    return out

PARTIES = []

# ---------------------------------------------------------------- 1
PARTIES.append({
 'num': '01', 'court': 'Architecture',
 'titre': 'Architecture générale et prérequis',
 'blocks': corps('01') + corps('02'),
})

# ---------------------------------------------------------------- 2
PARTIES.append({
 'num': '02', 'court': 'Module de visualisation',
 'titre': 'Le Module de Visualisation',
 'blocks': corps('03'),
})

# ---------------------------------------------------------------- 3
PARTIES.append({
 'num': '03', 'court': 'Base Historique et CMMA',
 'titre': 'La Base Historique et le calcul de la CMMA',
 'blocks': corps('04') + corps('06'),
})

# ---------------------------------------------------------------- 4
p4 = corps('05')
p4 += [
 h2('La session mensuelle, étape par étape'),
 para('Les trois chapitres qui suivent reprennent le déroulé décrit dans le guide '
      'd’utilisation. Ils ne répètent pas les gestes de l’officier : ils donnent, pour chaque '
      'étape, les feuilles, les formules et les procédures mises en jeu, dans l’ordre où elles '
      's’exécutent. C’est cet ordre qui explique le séquencement du code, et il se perdrait si '
      'les procédures n’étaient décrites qu’une à une.'),
]
for num, titre in [('07', 'Étape 1 — la saisie des bons de commande'),
                   ('08', 'Étape 2-A — le paramétrage et l’arbitrage district'),
                   ('09', 'Étape 2-B — le rapport et le circuit de validation du MCD'),
                   ('10', 'Étape 3 — finaliser et archiver')]:
    p4 += titrer(num, titre)
PARTIES.append({'num': '04', 'court': 'Application PCDD', 'titre': 'L’application PCDD', 'blocks': p4})

# ---------------------------------------------------------------- 5
PARTIES.append({
 'num': '05', 'court': 'Développement et maintenance',
 'titre': 'Développement et maintenance',
 'blocks': corps('11') + corps('12'),
})

# ---------------------------------------------------------------- 6
CONTROLES = {
 't': 'table',
 'head': ['Contrôle', 'Condition détectée', 'Signal', 'Action attendue'],
 'rows': [
  ['Saisie des BC — produits renseignés',
   'Une quantité manque pour au moins un produit du référentiel',
   'Le bouton « Valider la saisie » ne s’affiche pas',
   'Compléter les quantités manquantes'],
  ['Saisie des BC — valeurs entières',
   'Une quantité comporte une décimale ou du texte',
   'Le bouton « Valider la saisie » ne s’affiche pas',
   'Corriger la valeur'],
  ['Saisie des BC — doublon',
   'Un BC existe déjà pour ce CSI et cette période',
   'Message « Doublon détecté », saisie refusée',
   'Reprendre la saisie existante plutôt que d’en créer une'],
  ['Saisie des BC — période antérieure',
   'Une opération d’une période précédente demeure dans « Opérations en cours »',
   'Validation bloquée',
   'Terminer le pilotage et l’archivage de la période précédente'],
  ['Arbitrage — colonne de saisie complète',
   'Une cellule de la colonne `L` est vide',
   'Message « Veuillez renseigner toutes les cellules de la colonne L »',
   'Compléter la colonne des quantités validées'],
  ['Arbitrage — disponibilité en MdS',
   'La cellule `O12` est vide',
   'Message, et sélection automatique de `O12`',
   'Saisir la couverture visée'],
  ['Arbitrage — stock net final',
   '`M14` est négatif : le total validé dépasse le stock distribuable',
   'Message « Stock insuffisant pour la distribution » ; le produit n’est pas ajouté au rapport',
   'Réduire le MdS cible ou les quantités validées'],
  ['Arbitrage — produit déjà au rapport',
   'Le produit figure déjà dans `Tbl_Rapport_CMD`',
   'Message « Doublon détecté pour ce produit »',
   'Supprimer l’ancienne ligne avant de relancer'],
  ['Rapport final — tous produits arbitrés',
   'Un des huit produits n’a pas été ajouté au rapport (`P3` ≠ OK)',
   'Aucun message : les boutons du rapport PDF et de l’archivage restent masqués',
   'Arbitrer et ajouter les produits restants'],
  ['Export PDF — nom de fichier',
   'La cellule `M1` est vide',
   'Message « Le nom du fichier est vide »',
   'Vérifier la feuille de rapport'],
  ['Export PDF — dossier de sortie',
   'Le dossier `Rapport_MCD_PDF\\` n’existe pas',
   'Message « dossier introuvable »',
   'Créer le dossier, ou corriger le chemin du § 01'],
  ['Sauvegarde — enregistrement existant',
   'La clé concaténée figure déjà dans la Base Historique (colonne `AA`)',
   'Signal « Doublons »',
   'Vérifier la période ; supprimer l’enregistrement avant de resauvegarder'],
 ]}

p6 = [
 lede('Les contrôles du système ne se ressemblent pas : certains affichent un message, '
      'd’autres masquent un bouton sans rien dire. Le tableau ci-dessous les rassemble, avec '
      'la condition détectée, le signal produit et le geste attendu.'),
 CONTROLES,
 note('stop', 'Deux contrôles, deux comportements',
  'Le contrôle du stock net final affiche un message explicite : l’officier sait pourquoi il '
  'est arrêté. Le contrôle du rapport final, lui, se contente de masquer les boutons. Aucun '
  'message n’est émis.',
  'C’est la source d’appel la plus probable au démarrage : un officier qui cherche le bouton '
  'du rapport alors qu’il devrait chercher le produit non arbitré. Le guide d’utilisation et '
  'la fiche opératoire le signalent tous deux.'),
 h2('Tests de non-régression après modification'),
 para('Toute intervention sur les formules de la CMMA, sur les plages figées ou sur les '
      'procédures d’archivage doit être suivie des vérifications ci-dessous, sur une copie et '
      'non sur le classeur de l’officier.'),
 {'t': 'ol', 'items': [
   'Ouvrir le PCDD et confirmer que l’actualisation Power Query se termine sans message.',
   'Sur un CSI dont l’historique est complet, vérifier que la CMMA affichée est identique à '
   'celle relevée avant la modification.',
   'Sur un CSI sans historique récent, vérifier que le repli N−1 s’applique et que la mention '
   '« CMMA non disp » apparaît lorsque aucune référence n’existe.',
   'Saisir un BC, le valider, et confirmer que la ligne arrive dans « Opérations en cours » et '
   'que la zone de saisie se vide.',
   'Arbitrer les huit produits et confirmer que les boutons du rapport et de l’archivage '
   'apparaissent seulement après le huitième.',
   'Produire le PDF, puis archiver, et vérifier que le solde reporté en `M9` correspond au '
   'solde restant du mois archivé.',
 ]},
 note('warn', 'Avant toute modification',
  'Dupliquer les trois classeurs et travailler sur la copie. L’archivage est irréversible : '
  'une fois la session clôturée, les données quittent les tables de travail et le mois ne peut '
  'plus être repris.'),
]
PARTIES.append({'num': '06', 'court': 'Contrôles, dépannage et tests',
                'titre': 'Contrôles, dépannage et tests', 'blocks': p6})

d['SECTIONS'] = PARTIES
d['META']['chiffres'] = [['Parties', '6'], ['Classeurs', '3'],
                         ['Procédures VBA', '36'], ['Contrôles recensés', '12']]
json.dump(d, open('/home/claude/gen/contenu.json', 'w', encoding='utf8'),
          ensure_ascii=False, indent=1)
for p in PARTIES:
    print(f"{p['num']}  {p['titre'][:48]:50s} {len(p['blocks'])} blocs")
