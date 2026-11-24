# Guide développeur PCDD

Chaîne de production du **Guide développeur du PCDD** (Plan de Contrôle de
Distribution des Districts) — projet GHSC-PSM Niger, Chemonics International.

Le contenu vit dans un seul fichier. Deux moteurs en tirent le Word et la page
web, qui ne peuvent donc pas diverger.

## Construire

```bash
npm install
npm run dist
```

Produit dans `dist/` :

| Fichier | Usage |
|---|---|
| `Guide_developpeur_PCDD.docx` | document Word — relecture, corrections suivies, diffusion |
| `Guide_developpeur_PCDD.html` | page autonome — consultation, dépôt sur Drive |
| `guide.html` | fragment sans en-tête HTML, pour publication dans un conteneur |

`dist/` n'est pas versionné : les livrables se régénèrent.

## Modifier le guide

Tout passe par **`contenu.json`**. Ne pas éditer le Word ou le HTML : ils sont
écrasés à la construction suivante.

Le fichier contient les métadonnées puis six parties, chacune une liste de blocs
typés :

| Type | Rendu |
|---|---|
| `lede` | chapeau de partie |
| `p` | paragraphe |
| `h2` | titre de chapitre |
| `h3x` | sous-titre |
| `ul`, `ol` | listes |
| `note` | encart — `kind` : `info`, `warn`, `stop`, `retenir` |
| `fiche` | encadré titre / sous-titre / paires libellé-valeur |
| `code` | bloc de code monospace, avec légende |
| `table` | tableau — `head` puis `rows` |

Dans le texte : `` `code` ``, `**gras**`, `*italique*`. Les largeurs de colonnes
des tableaux sont calculées automatiquement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `contenu.json` | **la source** — tout le contenu du guide |
| `render-html.js` | rendu web : sommaire, encarts, blocs de code |
| `render-docx.js` | rendu Word : charte GHSC-PSM, tableaux natifs, texte modifiable |
| `wrap.py` | enveloppe le fragment HTML en page autonome et nomme les livrables |
| `style.css` | feuille de style du rendu web |
| `logo_*.png` / `logo_*.txt` | logos — PNG pour Word, data-URI pour le web |
| `historique/` | scripts de transformation déjà appliqués, conservés pour mémoire |

## Charte

Bleu USG `#002F6C`, bleu clair `#0067B9`, rouge USG `#BA0C2F`, ambre `#C8701A`,
vert `#2E7D4F`. Titres en Gill Sans MT, texte en Calibri, code en Consolas.
Les valeurs sont dans `style.css` pour le web et en tête de `render-docx.js`
pour le Word — les deux doivent rester alignées.

## Reconstruction de secours

`historique/extract.py` relit un guide HTML déjà produit et en reconstitue
`contenu.json`. Il a servi en novembre 2026, après la perte des sources
d'origine. Il reste utilisable si `contenu.json` venait à disparaître alors
qu'un rendu HTML subsiste.

## Historique

- **Novembre 2026** — réorganisation en six parties par composant, à la suite de
  la relecture de Boubacar Garba. Intégration de la version d'Excel requise, des
  colonnes de contrôle du Module de Visualisation, et du tableau des douze
  contrôles bloquants. Voir `historique/`.
