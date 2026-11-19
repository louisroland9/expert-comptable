# 07 — Workflow git

## Principe

Le dépôt applique **Conventional Commits**, des **commits atomiques** et une **branche par
feature**. Outillage : `pre-commit` + `commitizen`, pilotés par **uv**.

Les interdits git sont dans le socle (`.clinerules/00-socle.md`, I1/I4/I9) ; règle d'or :
**un commit = un changement logique**.

## R1 — Bootstrap (une fois par clone)

```bash
uv sync && uv run pre-commit install --install-hooks && git config commit.template .gitmessage
```

Le `core.hooksPath` est **local et non versionné** : un clone neuf relance ces commandes.

## R2 — Une branche par feature

```bash
scripts/creer_branche.sh feat calcul-tva
```

| Préfixe | Usage |
|---|---|
| `feat/<slug>` | Nouvelle capacité du harnais (script, calcul, mapping) |
| `fix/<slug>` | Correction d'un calcul, d'un mapping, d'un bug |
| `chore/<slug>` | Outillage, dépendances, tâches internes |
| `docs/<slug>` | Documentation seule (README, `.clinerules/`, `docs/procedures/`, `memory-bank/`) |

Le script refuse un arbre sale, normalise le slug, part de `main` et **ne pousse pas**.

### R2.1 — La branche est TOUJOURS obligatoire

**Aucune exception** : `1 tâche = 1 branche = N commits atomiques`. Même pour une virgule,
une faute de frappe ou un titre de README — un changement d'un caractère passe par
`chore/…`. Le préfixe suit le tableau du R2.

> **Corollaire** : si aucun slug raisonnable ne vient, la tâche n'est pas un changement
> logique unique — la re-découper.

### R2.2 — Branche précédente non mergée : prévenir et demander

Avant de créer une branche, **inspecter l'état** :

```bash
git for-each-ref --format='%(refname:short) %(contents:subject)' refs/heads
git log --oneline main..<branche-en-attente>
```

S'il existe **au moins une branche locale non mergée dans `main`**, l'agent **s'arrête,
prévient et demande** : « `<branche>` n'est pas mergée dans `main` (N commits en attente).
Je pars de `main`, ou j'empile sur `<branche>` ? » — puis **attend la réponse** avant tout
`checkout`, `switch` ou `commit`.

| Situation | Comportement |
|---|---|
| Aucune branche en attente | Créer depuis `main` et poursuivre |
| Branche(s) en attente | **Stopper, prévenir, demander**, attendre |
| « pars de `main` » | Créer depuis `main`, signaler le risque de conflit |
| « empile » | Créer depuis la branche indiquée, noter la dépendance |

> Le point de départ retenu est **explicité** dans le compte rendu de fin de tâche.

## R3 — Format de commit

```
<type>(<scope>): <description à l'infinitif, ≤ 72 caractères>

[corps : POURQUOI, pas COMMENT]

[#issue / A{n} / Q{n}]
```

- **Types :** `feat` `fix` `chore` `docs` `refactor` `test` `build` `ci` `perf` ; description
  en **français**, à l'infinitif, sans ponctuation finale ni majuscule initiale.
- **Scopes usuels (non bloquants) :** `fec` `tva` `equilibre` `amortissements` `mapping`
  `memoire` `regles` `qonto` `outillage` ; validés par `cz check` (hook `commit-msg`).

## R4 — Atomicité

1. **Un commit = un changement logique** complet et cohérent ; ne pas mélanger `refactor`
   et `feat`, ni `docs` et code (sauf si la doc fait partie du changement).
2. Le dépôt reste **fonctionnel à chaque commit** ; découper avec `git add -p` si plusieurs
   changements cohabitent.
3. Un livrable fiscal et son `.meta.json` ne se committent jamais.

## R5 — Cycle de vie d'une branche

1. Vérifier les branches non mergées (**R2.2**) et **demander** si besoin
2. `scripts/creer_branche.sh <prefixe> <slug>` ; commits atomiques
3. `uv run pre-commit run --all-files` avant de rendre la main
4. **Rendre la main** : branche, **point de départ**, commits, tests. **Ne pas pousser ni
   merger** — l'utilisateur merge (squash) puis supprime la branche.

## R6 — Cohérence avec les autres règles

| Règle | Rappel appliqué au git |
|---|---|
| 01 (persona, doublon) | Un écart avec l'EC se documente dans `memory-bank/cabinet-doublon.md`, **dans le même commit**. |
| 02 (Qonto) | Aucun snapshot ne sort du workspace : ne pas committer `qonto-exports/`. |
| 03 (calculs) | `.meta.json` = fichier compagnon généré : **jamais versionné**. |
| 05 (mémoire) | Décision structurante ⇒ `cabinet-doublon.md` mis à jour dans le même commit. |

## R7 — Ce que l'agent fait et ne fait pas

- **Autorisé** : `git status`, `diff`, `log`, `show`, `switch -c`, `add -p`,
  `restore --staged` ; `commit` sur une branche `feat|fix|chore|docs` ;
  `uv run pre-commit run --all-files`.
- **Interdit** : `git push` (toutes formes), `commit` sur `main`, `reset --hard` sans
  validation, `rebase` sur une branche poussée, modifier `qonto-exports/` ou
  `reference-expert-comptable/`.
- Aucune donnée Qonto ne sort du workspace : hooks en `repo: local`, rien de téléchargé.
