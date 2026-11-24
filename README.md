# PCDD — Plan de Contrôle de Distribution des Districts

Documentation du **PCDD**, le module Excel par lequel les districts sanitaires
du Niger contrôlent les quantités d'intrants antipaludiques commandées par les
formations sanitaires.

Le PCDD est un module analytique posé sur les données du DHIS2. Il n'est pas un
système d'information concurrent : il ne produit aucune donnée primaire, n'en
corrige aucune, et n'en transmet aucune — les fichiers restent sur le poste de
l'équipe du district. Les fonctions qu'il assure ont vocation à être reprises
par l'eSIGL lorsque celui-ci sera déployé dans les districts.

Projet GHSC-PSM Niger · Chemonics International · financement du gouvernement
des États-Unis, contrat n° AID-OAA-I-15-0004.

## Les documents

Quatre documents, chacun pour un usage et un lecteur distincts.

| Document | Pour qui | Formats |
|---|---|---|
| [Fiche opératoire](docs/Fiche_operatoire_PCDD.docx) | l'officier, au poste de travail | Word — 4 pages, 2 feuilles recto-verso |
| [Guide d'utilisation](docs/Guide_utilisation_PCDD.docx) | l'officier, avant la première session | Word · [HTML](docs/Guide_utilisation_PCDD.html) |
| [Note méthodologique](docs/Note_methodologique_PCDD.docx) | responsables de district, partenaires institutionnels | Word · [HTML](docs/Note_methodologique_PCDD.html) |
| [Guide du développeur](docs/Guide_developpeur_PCDD.docx) | qui reprend le système | Word · [HTML](docs/Guide_developpeur_PCDD.html) |

**La fiche opératoire** tient en deux feuilles recto-verso : les trois étapes,
les vérifications préalables, le code couleur, les contrôles bloquants. Elle est
faite pour être imprimée et affichée, d'où l'absence de version web.

**Le guide d'utilisation** détaille chaque étape avec les copies d'écran. Sa
version HTML se lit page par page, avec une barre de progression — l'officier
le parcourt comme un module de formation.

**La note méthodologique** expose le contexte, l'origine des données et les
règles de calcul : consommation ajustée des jours de rupture, sélection
saisonnière des mois de référence, repli sur l'année précédente. C'est le
document à produire quand un chiffre affiché est contesté.

**Le guide du développeur** décrit le classeur de référence et sa configuration
district par district, en six parties par composant. Il est le seul dont la
chaîne de production figure ici.

## La chaîne de production

`chaine/guide-developpeur/` contient la source du guide du développeur et les
deux moteurs qui en tirent le Word et la page web. Le contenu vit dans un seul
fichier, `contenu.json` ; les deux rendus ne peuvent donc pas diverger.

```bash
cd chaine/guide-developpeur
npm install
npm run dist
```

Les livrables sortent dans `dist/` et sont à recopier dans `docs/`.

**Les fichiers de `docs/` sont des produits de construction.** Corriger le Word
ou le HTML ne sert à rien pour le guide du développeur : le build suivant les
écrase. Toute correction de fond passe par `contenu.json`. Le Word reste
annotable en corrections suivies pour une relecture — c'est son usage — mais les
corrections acceptées doivent remonter dans la source.

Les trois autres documents n'ont pas encore leur chaîne dans ce dépôt : leurs
planches sont dessinées par un moteur distinct, à reconstruire.

## Le module

Le PCDD repose sur trois classeurs qui communiquent par fichier interposé :

1. **Module de Visualisation** — import de l'export DHIS2, contrôle de
   complétude et de cohérence, capture des photos de complétude, écriture vers
   la Base Historique.
2. **Base Historique** — mémoire mensuelle par site, produit et période. C'est
   ici qu'est calculée la consommation ajustée des jours de rupture.
3. **PCDD** — sélection des mois de référence, calcul de la CMMA, arbitrage des
   quantités à distribuer, rapport et archivage.

Microsoft 365 est requis : les classeurs reposent sur `FILTRE`, `UNIQUE`,
`TRIER`, `RECHERCHEX`, `LET` et `CHOISIRCOLS`, qui n'existent pas dans les
versions antérieures d'Excel.

Chaque district travaille sur sa propre copie des trois fichiers. Les chemins
d'accès sont inscrits dans le code : deux littéraux dans le PCDD, sept dans le
Module de Visualisation. La liste complète figure au § 1 du guide du développeur.

## Crédits

Développement des classeurs Excel : Boubacar Garba.
Conception de la logique analytique et de la documentation : Frédérick Persoons.
