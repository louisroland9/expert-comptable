# qonto-exports

Dépôt des **snapshots bruts** extraits du serveur **MCP Qonto**.

## Règle d'or

> **Ces fichiers sont la source de vérité. Ils ne sont JAMAIS modifiés,
> renommés ou supprimés.**

Tout script Python lit ces fichiers en **lecture seule**. Une nouvelle extraction
produit un **nouveau fichier** (`_v2`, `_v3`…), jamais un écrasement.

## Nommage

```
qonto-exports/{type}_{AAAA-MM}.json      # premier snapshot du mois
qonto-exports/{type}_{AAAA-MM}_v2.json   # extraction corrective
```

| Type | Contenu | Outil MCP source |
|---|---|---|
| `transactions` | Transactions du compte bancaire | `list_transactions` |
| `balance` | Soldes des comptes | `list_bank_accounts` |
| `statements` | Relevés mensuels | `list_statements` |
| `attachments` | Liste des justificatifs | `list_transaction_attachments` |
| `factures-clients` | Factures clients | `list_client_invoices` |
| `factures-fournisseurs` | Factures fournisseurs | `list_supplier_invoices` |
| `clients` | Référentiel clients | `list_clients` |
| `organisation` | Identité de l'organisation | `list_organizations` |

## En-tête `_meta` obligatoire

Chaque JSON contient un bloc de traçabilité :

```json
{
  "_meta": {
    "source": "mcp:qonto",
    "outil": "list_transactions",
    "extrait_le": "2026-11-17T16:30:00+01:00",
    "organisation_id": "…",
    "filtres": { "status": ["completed"], "bank_account_id": "…" },
    "nb_enregistrements": 42
  },
  "transactions": [ ... ]
}
```

## Confidentialité

⚠️ Ce dossier est **exclu du versionnement Git** (`.gitignore`). Il contient des
données bancaires : ne jamais le commiter, ne jamais le partager, ne jamais le
copier hors du poste de travail.

## Fichiers attendus (état actuel)

| Fichier | Statut |
|---|---|
| — | ⏳ Aucun snapshot extrait pour l'instant |
