# 07 — Workflow git

## Principe

Le dépôt applique **Conventional Commits**, des **commits atomiques**, et une
**branche par feature**. Outillage : `pre-commit` + `commitizen`, pilotés par **uv**.

| Interdit | Règle |
|---|---|
| 🔴 `git push` par l'agent | **L'utilisateur pousse lui-même.** Aucune exception. |
| 🔴 Committer sur `main` | Toujours créer `feat/…`, `fix/…` ou `chore/…` d'abord. |
| 🔴 Versionner une donnée financière | `qonto-exports/`, `reference-expert-comptable/`, `exports-fiscaux/`, `*.pdf`, `*.meta.json` |
| 🔴 Historique réécrit sur une branche partagée | `push --force` interdit sauf demande explicite. |
| 🔴 Commits fourre-tout | Un commit = un changement logique. |

## R1 — Bootstrap (une fois par clone)

```bash
uv sync
uv run pre-commit install --install-hooks
git config commit.template .gitmessage
```

Le `core.hooksPath` posé par pre-commit est **local et non versionné** : un clone
neuf doit relancer les commandes ci-dessus.

## R2 — Une branche par feature

```bash
scripts/creer_branche.sh feat calcul-tva
```

| Préfixe | Usage |
|---|---|
| `feat/<slug>` | Nouvelle capacité du harnais (script, calcul, mapping) |
| `fix/<slug>` | Correction d'un calcul, d'un mapping, d'un bug |
| `chore/<slug>` | Outillage, dépendances, tâches internes |

Le script refuse un arbre sale, normalise le slug, part de `main` et **ne pousse pas**.

## R3 — Format de commit

```
<type>(<scope>): <description à l'infinitif, ≤ 72 caractères>

[corps : POURQUOI, pas COMMENT]

[#issue / A{n} / Q{n}]
```

- **Types :** `feat` `fix` `chore` `docs` `refactor` `test` `build` `ci` `perf`
- **Scopes usuels (non bloquants) :** `fec` `tva` `equilibre` `amortissements`
  `mapping` `memoire` `regles` `qonto` `outillage`
- Description en **français**, à l'infinitif, sans ponctuation finale, sans majuscule initiale.
- Validation automatique : `cz check` (hook `commit-msg`).

## R4 — Atomicité

1. **Un commit = un changement logique** complet et cohérent.
2. Ne **jamais** mélanger `refactor` et `feat`, ni `docs` et changement de code
   (sauf si la doc fait partie intégrante du changement).
3. Le dépôt doit rester **fonctionnel à chaque commit**.
4. Découper avec `git add -p` si plusieurs changements cohabitent.
5. Un livrable fiscal et son `.meta.json` ne se committent pas (règle R6/03).

## R5 — Cycle de vie d'une branche

```
main ──► chore/outillage-git ──► (commits atomiques) ──► validation ──► UTILISATEUR merges
```

1. `scripts/creer_branche.sh <prefixe> <slug>`
2. Commits atomiques, un par changement logique
3. Contrôles avant de rendre la main :
   `uv run pre-commit run --all-files`
4. **Rendre la main** : indiquer la branche, les commits, les tests exécutés.
   **Ne pas pousser, ne pas merger.**
5. L'utilisateur merge (squash) puis supprime la branche.

## R6 — Cohérence avec les autres règles

| Règle | Rappel appliqué au git |
|---|---|
| 01 (persona, doublon) | Un écart avec l'EC se documente dans `memory-bank/cabinet-doublon.md` — **dans le même commit** que le changement. |
| 02 (Qonto) | Aucun snapshot ne sort du workspace : interdit de committer `qonto-exports/`. |
| 03 (calculs Python) | Un `.meta.json` est un fichier compagnon généré : **jamais versionné**. |
| 05 (mémoire) | Une décision structurante ⇒ mise à jour de `cabinet-doublon.md` dans le commit correspondant. |

## R7 — Ce que l'agent fait et ne fait pas

| Autorise | Interdit |
|---|---|
| `git status`, `git diff`, `git log`, `git show` | `git push` (toutes formes) |
| `git switch -c`, `git add -p` | `git commit` sur `main` |
| `git commit` sur branche `feat\|fix\|chore` | `git reset --hard` sans validation |
| `git restore --staged <fichier>` | `git rebase` sur une branche poussée |
| `uv run pre-commit run --all-files` | Modification d'un fichier de `qonto-exports/` ou `reference-expert-comptable/` |

> Aucune donnée Qonto ne sort du workspace vers un service tiers : tout hook reste
> en `repo: local`, rien n'est téléchargé depuis le réseau.
