# Pull Request — LR Data

> Branche source : `<type>/<slug>` → cible : `main`
> Le merge est fait **par le propriétaire du dépôt** (l'agent ne pousse ni ne merge).

## Objet

<!-- Une phrase : quel changement logique, et pourquoi. -->

## Type de changement

- [ ] `feat` — nouvelle capacité du harnais
- [ ] `fix` — correction d'un calcul, d'un mapping, d'un bug
- [ ] `chore` — outillage, dépendances
- [ ] `docs` — documentation (README, `.clinerules/`, `memory-bank/`)
- [ ] `refactor` — sans changement de comportement
- [ ] `test` — tests
- [ ] `build` / `ci` — outillage, hooks

## Commits inclus

<!-- Un commit = un changement logique. Lister les messages. -->

```
chore(outillage): ...
```

## Contrôles comptables (règle 03)

- [ ] Aucun montant calculé sans `Decimal` (jamais de `float`)
- [ ] Aucun calcul de tête : toute somme provient d'une sortie de script citée
- [ ] Contrôle d'équilibre passé (par journal, par écriture, global)
- [ ] Code de sortie attendu respecté (0 / 1 / 2 / 3)
- [ ] `.meta.json` produit dans `exports-fiscaux/` (et **non versionné**)
- [ ] Scripts toujours fonctionnels en **stdlib pure** (règle R3/03)

## Contrôles de sources (règles R4/03, 02)

- [ ] Aucun fichier de `qonto-exports/` modifié, renommé ou supprimé
- [ ] Aucun fichier de `reference-expert-comptable/` modifié
- [ ] Aucune donnée financière dans le diff (`git diff --cached --name-only`)
- [ ] Aucun justificatif `.pdf` ni `.meta.json` committé

## Traçabilité du doublon (règles 01, 05)

- [ ] Les écarts avec l'expert-comptable sont consignés dans `memory-bank/cabinet-doublon.md`
- [ ] Les comptes PCG cités le sont avec **numéro + intitulé exacts** (règle R1/01)
- [ ] Une décision structurante suit le format `D-{NN}` (règle R6/05)
- [ ] Aucun montant inventé ; un montant estimé porte la mention `⚠️ ESTIMÉ — À CONFIRMER`

## Documentation (règle 08)

- [ ] Le changement ne touche ni `scripts/`, ni `.clinerules/`, ni `memory-bank/`,
      ni `pyproject.toml` → `README.md` inchangé (légitime)
- [ ] **OU** les sources ont changé **et** `README.md` est mis à jour dans le **même
      commit** (§ 2 Arborescence, § 4 Scripts, § 3 Installation)
- [ ] Le README ne documente **aucun** script ni entry point supprimé/renommé
- [ ] L'avertissement `readme-a-jour` est soit **résolu**, soit **explicitement ignoré**
      et justifié ci-dessous

## Alertes déclenchées par ce changement

- [ ] Aucune
- [ ] A1 — compte courant d'associé `455100` **débiteur** (🔴 bloquant)
- [ ] A2 — transaction sans justificatif (TVA non déductible par défaut)
- [ ] A3 — TVA non récupérable
- [ ] A4 — autoliquidation UE (`445200`, mention obligatoire)
- [ ] A5 — achat hors UE (SaaS US…)
- [ ] A6 — formation / enseignement (exonération art. 261-4-4° CGI à confirmer)
- [ ] A7 — libération du capital à confirmer
- [ ] A8 — dépense > 500 € HT (immobilisation `218300` à valider)
- [ ] A9 — CFE à provisionner
- [ ] A10 — justificatif non conforme e-invoicing

## Périmètre temporel (règle R4/01)

- [ ] Toutes les écritures sont **postérieures au 09/06/2026**
- [ ] Les écritures couvertes restent dans le périmètre `09/06/2026 → 31/12/2026`

## Vérifications exécutées

```bash
uv run pre-commit run --all-files
python3 scripts/verifier_equilibre.py
```

<!-- Reproduire la sortie console et indiquer le code de sortie. -->

## Points ouverts / à revoir

<!-- Renvoyer vers memory-bank/cabinet-doublon.md (Q{n} / D-{NN}). -->
