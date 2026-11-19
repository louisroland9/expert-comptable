# 03 — Règles de calcul (Python)

## R1 — Interdiction absolue du calcul mental

**Aucun** montant, total, TVA, amortissement, solde ou écart ne doit être calculé « de
tête » ou par le modèle. **Tout** calcul passe par un script Python exécuté, dont la
sortie est citée comme source.

- ❌ « Le total fait environ 12 345 €. »
- ✅ « `uv run scripts/calculer_tva.py --mois 2026-11` → collectée 2 310,00 € (sortie
  console reproduite ci-dessous). »

## R2 — Arithmétique exacte

- **`decimal.Decimal`** obligatoire pour tout montant en euros. **Jamais de `float`**
  pour un solde, une TVA ou un total.
- Quantification : `Decimal(...).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- Tolérance d'équilibre : **`Decimal("0.00"))`** — zéro écart toléré. Si un arrondi
  est inévitable, il est **matérialisé par une ligne d'OD de régularisation**, jamais
  absorbé silencieusement.
- Taux : `Decimal("0.20")`, `Decimal("0.10")`, `Decimal("0.055")`, `Decimal("0.021")`,
  `Decimal("0.15")`, `Decimal("0.25")`. Jamais `0.2` en littéral flottant seul dans un
  calcul monétaire.

## R3 — Environnement d'exécution

Projet géré avec **`uv`** (`pyproject.toml`) et Python **≥ 3.12** (3.12.3 en place).

```bash
uv venv                                   # crée .venv/  (une seule fois)
uv pip install -e .                       # ou: uv pip install pandas openpyxl
uv run scripts/verifier_equilibre.py      # exécution
```

Règle de robustesse : **`scripts/verifier_equilibre.py`, `generer_fec.py` et
`comparer_avec_ec.py` doivent fonctionner en stdlib pure** (aucune dépendance externe).
`pandas` n'est autorisé que là où il apporte un gain réel (`calculer_tva.py`,
analyses), et jamais au prix de la perte du mode stdlib.

## R4 — Sources immuables

- `qonto-exports/` : **lecture seule** pour les scripts. Jamais de réécriture,
  renommage, troncature.
- `reference-expert-comptable/` : **lecture seule absolue**.
- Les sorties vont **exclusivement** dans `exports-fiscaux/` (ou `_travail/` pour les
  fichiers intermédiaires).
- Aucun script ne doit contenir de chemin absolu en dur vers le domicile d'un
  utilisateur : chemins relatifs à la racine du projet, surchargeables par `--dir`.

## R5 — Contrôle d'équilibre obligatoire

Après **toute** génération d'écritures :

1. **Par journal** : Σ Débit == Σ Crédit
2. **Par écriture** : Σ Débit == Σ Crédit
3. **Global** : Σ Débit == Σ Crédit sur la totalité du jeu
4. **Format** : chaque montant est un `Decimal` à 2 décimales, au format français
   (virgule) à l'affichage et dans le FEC.

Un déséquilibre **bloque** la suite : le script retourne un **code de sortie non nul**
et n'écrit aucun livrable validé.

## R6 — Traçabilité

Tout script produisant un livrable écrit un fichier compagnon `.meta.json` :

```json
{
  "script": "generer_fec.py",
  "version": "1.0.0",
  "execution": "2026-11-17T15:40:00+01:00",
  "entrees": ["qonto-exports/transactions_2026-06.json", ...],
  "sha256_entrees": { "qonto-exports/transactions_2026-06.json": "..." },
  "parametres": { "exercice": "2026", "perimetre": "2026-06-09/2026-12-31" },
  "lignes_produites": 421,
  "total_debit": "123456.78",
  "total_credit": "123456.78",
  "equilibre": true
}
```

## R7 — Codes de sortie

| Code | Signification |
|---|---|
| `0` | Succès, équilibre vérifié |
| `1` | Succès technique mais **anomalies détectées** (avertissements) |
| `2` | **Déséquilibre** ou erreur de structure → livrable non validé |
| `3` | Erreur d'entrée (fichier manquant, JSON invalide) |

## R8 — Interdictions

- ❌ Écraser un fichier source
- ❌ Calculer un montant sans l'afficher avec 2 décimales
- ❌ Utiliser `round()` Python natif sur un montant (utiliser `Decimal.quantize`)
- ❌ « Corriger » un déséquilibre en modifiant un montant d'écriture sans écriture
  de régularisation explicite et documentée
- ❌ Écrire un livrable dans `exports-fiscaux/` si le contrôle d'équilibre échoue
