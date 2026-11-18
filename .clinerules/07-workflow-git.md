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

### R2.1 — La branche est TOUJOURS obligatoire

**Aucune exception.** Même pour une virgule, une faute de frappe, un titre dans un
README : toute tâche passe par une branche dédiée.

```
1 tâche  =  1 branche  =  N commits atomiques
```

Il est **interdit** de committer directement sur `main`, quelle que soit la taille
du changement. Un changement d'un seul caractère passe par `chore/…`.

| Cas | Branche à créer |
|---|---|
| Ajouter une capacité (script, calcul) | `feat/<slug>` |
| Corriger un calcul, un mapping, un bug | `fix/<slug>` |
| Outillage, dépendances, doc, typo, virgule | `chore/<slug>` |

> **Corollaire** : si aucun slug raisonnable ne vient, c'est le signe que la tâche
> n'est pas un changement logique unique. La re-découper.

### R2.2 — Branche précédente non mergée : prévenir et demander

L'agent **ne décide pas seul** du point de départ d'une nouvelle tâche. Avant de
créer une branche, il **inspecte l'état** :

```bash
git for-each-ref --format='%(refname:short) %(contents:subject)' refs/heads
git log --oneline main..<branche-en-attente>
```

S'il existe **au moins une branche locale non mergée dans `main`**, l'agent
**s'arrête et demande explicitement** à l'utilisateur :

> « La branche `<branche>` n'est pas mergée dans `main` (N commits en attente).
> Je pars de `main`, ou j'empile sur `<branche>` ? »

Il **attend la réponse** avant tout `checkout`, `switch` ou `commit`.

| Situation | Comportement attendu |
|---|---|
| Aucune branche en attente | Créer la branche depuis `main` et poursuivre |
| Branche(s) en attente | **Stopper, prévenir, demander**, puis attendre |
| L'utilisateur dit « pars de `main` » | Créer depuis `main`, signaler le risque de conflit |
| L'utilisateur dit « empile » | Créer depuis la branche indiquée, noter la dépendance |

> ⚠️ **Règle de restitution** : le point de départ retenu est **explicité** dans le
> compte rendu de fin de tâche (« branche créée depuis `main` » / « empilée sur
> `<branche>` »).

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

1. Vérifier les branches non mergées (cf. **R2.2**) et **demander** si besoin
2. `scripts/creer_branche.sh <prefixe> <slug>`
3. Commits atomiques, un par changement logique
4. Contrôles avant de rendre la main :
   `uv run pre-commit run --all-files`
5. **Rendre la main** : indiquer la branche, son **point de départ**, les commits, les
   tests exécutés. **Ne pas pousser, ne pas merger.**
6. L'utilisateur merge (squash) puis supprime la branche.

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
