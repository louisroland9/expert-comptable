# 08 — Documentation (README)

## Principe

`README.md` (racine) est la **porte d'entrée du harnais** : périmètre, fiche d'identité,
arborescence, installation, scripts et codes de sortie, workflow git, règles d'or. Il
**reste faux dès qu'une source bouge sans lui** → mise à jour **dans le même commit** que
le changement de source.

## R1 — Déclencheurs de mise à jour

Un commit **doit** mettre à jour `README.md` lorsqu'il touche :

| Chemin modifié | Section du README à revoir |
|---|---|
| `scripts/**` (ajout, renommage, suppression) | § 2 Arborescence, § 4 Scripts |
| `pyproject.toml` (`[project.scripts]`, dépendances, Python) | § 3 Installation, § 4 Scripts |
| `.clinerules/**` ou `docs/procedures/**` (ajout, renommage) | § 2 Arborescence, § 9 Références |
| `memory-bank/**` (ajout, renommage), dossier de travail renommé | § 2 Arborescence |
| Nouveau hook pre-commit | § 8 Maintenance |
| Paramètre juridique ou fiscal structurant | § 1 Périmètre |

Un changement purement **interne** (correction de calcul, réordonnancement de code) ne
touche pas le README : il décrit l'**interface**, pas l'implémentation.

## R2 — Garde-fou `readme-a-jour` (avertisseur, non bloquant)

Le hook local `readme-a-jour` surveille la zone de commit : si une **source**
(`scripts/`, `.clinerules/`, `docs/procedures/`, `memory-bank/` — fichiers à plat — ou
`pyproject.toml`) est touchée **sans** `README.md`, il **affiche un rappel** et
**n'échoue pas**.

- Ce n'est **pas** une censure : contournement volontaire `SKIP=readme-a-jour git commit …`.
- Le contrôle est **indicatif** : une mise à jour de `memory-bank/suivi-exercice.md`
  déclenche le rappel sans que le README ait à changer. L'agent **juge** et, si le README
  est correct, **ignore** l'avertissement en le mentionnant.

## R3 — Discipline de contenu

Style de la persona 01 : dense, factuel, sans blabla.

- Tableaux dès 2 champs structurés ; chiffres et comptes PCG exacts, jamais inventés.
- Contenu **daté et sourcé** quand il dépend d'une décision (`D-{NN}`, `Q{n}`, Kbis, snapshot).
- Les codes de sortie reflètent à l'identique `pyproject.toml` et les docstrings : le README
  ne contredit jamais le code.

## R4 — Vérification avant de rendre la main

```bash
uv run pre-commit run --all-files                    # inclut le hook readme-a-jour
uv run --help | head                                 # entry points documentés
ls scripts/ ; ls .clinerules docs/procedures/        # arborescence réelle vs README
```

1. L'**arborescence** du README (§ 2) correspond au `ls` réel.
2. Chaque script de `scripts/` et chaque `[project.scripts]` du `pyproject.toml` est
   documenté au § 4 (et inversement).

## R5 — Interdictions

- ❌ Laisser une section du README décrire un script **supprimé ou renommé**.
- ❌ Documenter un **entry point inexistant** dans `pyproject.toml`.
- ❌ Mettre à jour le README dans un commit **séparé** du changement de source
  (règle R4/07 — atomicité : la doc fait partie intégrante du changement).
