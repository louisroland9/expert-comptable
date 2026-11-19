# reference-expert-comptable

Dépôt des **livrables de l'expert-comptable (EC)**, utilisés pour la comparaison
en **mode doublon**.

## Règles

1. 🔒 **Lecture seule absolue** : ces fichiers ne sont jamais modifiés par l'agent.
2. 📁 Nommage recommandé : `{type}_{periode}.{ext}` (ex. `balance_2026-11.csv`).
3. ⚠️ Le dossier est **exclu du versionnement** (données confidentielles).

## Livrables attendus

| Livrable | Format attendu | Utilité | Reçu |
|---|---|---|---|
| **Balance générale** | CSV `compte;libelle;debit;credit` | Comparaison compte à compte | ❌ |
| **FEC** | TXT (18 colonnes, art. A.47 A-1) | Comparaison des écritures | ❌ |
| **CA3** déposées | PDF / CSV | Réconciliation TVA | ❌ |
| **Grand livre** | CSV / PDF | Analyse des imputations | ❌ |
| **Bilan / compte de résultat** | PDF | Contrôle des agrégats | ❌ |
| **Écritures d'ouverture** | CSV | Point de départ du doublon | ❌ |

## Format de balance accepté par `comparer_avec_ec.py`

**CSV** (séparateur `;`, `,`, tabulation ou `|` détecté automatiquement) :

```csv
compte;libelle;debit;credit
706000;Prestations de services;0,00;2000,00
445710;TVA collectee;0,00;400,00
```

**JSON** :

```json
{
  "comptes": [
    { "compte": "706000", "debit": "0.00", "credit": "2000.00" },
    { "compte": "445710", "debit": "0.00", "credit": "400.00" }
  ]
}
```

Les montants acceptent le point ou la virgule décimale.

## Utilisation

```bash
python3 scripts/comparer_avec_ec.py
```

- Sans balance déposée → **mode veille** (code 4), aucun écart inventé.
- Avec balance → rapport d'écarts par compte, qualifiés
  (`écriture absente chez l'EC`, `imputation différente`…).

## État actuel

> ⏳ **Aucun livrable déposé** (réponse utilisateur : « je n'ai rien pour l'instant »).
> Le module de comparaison tourne donc en veille.
