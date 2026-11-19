# 08 — Documentation (README)

## Principe

`README.md` (racine) est la **porte d'entrée du harnais** : il décrit le périmètre, la
fiche d'identité, l'arborescence, l'installation, les scripts et leurs codes de sortie,
le workflow git et les règles d'or.

Il **reste faux dès qu'une source bouge sans lui**. Cette règle impose donc sa mise à
jour **dans le même commit** que le changement de source.

## R1 — Déclencheurs de mise à jour

Un commit **doit** mettre à jour `README.md` lorsqu'il touche :

| Chemin modifié | Section du README à revoir |
|---|---|
| `scripts/**` (ajout, renommage, suppression) | § 2 Arborescence, § 4 Scripts |
| `pyproject.toml` (`[project.scripts]`, dépendances, Python) | § 3 Installation, § 4 Scripts |
| `.clinerules/**` (ajout / renommage d'une règle) | § 2 Arborescence, § 9 Références |
| `memory-bank/**` (ajout / renommage d'un fichier) | § 2 Arborescence |
| Renommage d'un dossier de travail (`qonto-exports/`, etc.) | § 2 Arborescence, § 6 Règles d'or |
| Nouveau script de hook, nouvelle garde-fou pre-commit | § 8 Maintenance |
| Changement de paramètre juridique/fiscal structurant | § 1 Périmètre |

> Le README n'est **pas** à mettre à jour pour un changement purement interne
> (correction de calcul dans `scripts/`, réordonnancement de code) : il décrit
> l'**interface** du harnais, pas son implémentation.

## R2 — Garde-fou `readme-a-jour` (avertisseur, non bloquant)

Un hook `pre-commit` local surveille les fichiers mis en zone de commit. Si des
**sources** (`scripts/`, `.clinerules/` à plat, `memory-bank/` à plat, `pyproject.toml`)
sont touchées **sans** `README.md`, il **affiche un rappel** — et **n'échoue pas**.

- Le hook **n'empêche jamais** un commit : c'est un **rappel**, pas une censure.
- Contournement volontaire : `SKIP=readme-a-jour git commit …`
- Le contrôle est **indicatif** : un commit touchant `memory-bank/suivi-exercice.md`
  (mise à jour courante) déclenche le rappel alors que le README n'a rien à changer.
  L'agent **juge** et, si le README est correct, **ignore** l'avertissement en le
  mentionnant dans le compte rendu.

## R3 — Discipline de contenu

Le README suit le **style de la persona 01** : dense, factuel, sans blabla.

- Tableaux dès qu'il y a ≥ 2 champs structurés.
- **Chiffres et comptes PCG exacts** (R1/01), jamais de valeur inventée (R2/01).
- Un contenu **daté** et **sourcé** quand il dépend d'une décision
  (`D-{NN}`, `Q{n}`, « Kbis 08/06/2026 », « snapshot Qonto »).
- Les **codes de sortie** (R7/03) sont reflétés à l'identique de `pyproject.toml` et des
  docstrings : le README ne peut pas contredire le code.

## R4 — Vérification avant de rendre la main

```bash
uv run pre-commit run --all-files      # inclut le hook readme-a-jour
uv run --help | head                   # vérifier les entry points documentés
ls scripts/                            # comparer avec la liste du README
```

1. L'**arborescence** du README (§ 2) correspond à `ls` réel.
2. Chaque script de `scripts/` a sa ligne au § 4.
3. Chaque `[project.scripts]` du `pyproject.toml` est documenté (et inversement).

## R5 — Interdictions

- ❌ Laisser une section du README décrire un script **supprimé ou renommé**.
- ❌ Documenter un **entry point inexistant** dans `pyproject.toml`.
- ❌ Mettre à jour le README dans un commit **séparé** du changement de source
  (règle R4/07 — atomicité : la doc fait partie intégrante du changement).
