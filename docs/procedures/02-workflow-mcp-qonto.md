# 02 — Workflow : serveur MCP Qonto

## Serveur

| Champ | Valeur |
|---|---|
| Nom | `qonto` |
| URL | `https://mcp.qonto.com/mcp` |
| Transport | HTTP (streamable) |
| Authentification | **OAuth** (fournisseur d'identité `developers.qonto.com`) |
| Portée | **1 organisation par autorisation** |

## Configuration Cline

Fichier : `/home/louis/.cline/data/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "qonto": {
      "type": "http",
      "url": "https://mcp.qonto.com/mcp",
      "disabled": false,
      "autoApprove": [
        "list_organizations",
        "list_bank_accounts",
        "list_transactions",
        "get_transaction",
        "list_statements",
        "get_statement",
        "list_transaction_attachments",
        "get_attachment",
        "list_clients",
        "list_client_invoices",
        "list_supplier_invoices"
      ]
    }
  }
}
```

> **`autoApprove` ne contient QUE des outils de lecture.** Aucun outil d'écriture
> (création/envoi de facture, virement, carte) n'est auto-approuvé.

## Outils autorisés (lecture seule)

| Outil | Rôle |
|---|---|
| `list_organizations` | Identifier l'organisation connectée |
| `list_bank_accounts` | Soldes et liste des comptes |
| `list_transactions` | Transactions paginées (filtres dates, statut, compte) |
| `get_transaction` | Détail d'une transaction |
| `list_statements` | Relevés mensuels |
| `get_statement` | Relevé unitaire |
| `list_transaction_attachments` | **Justificatifs attachés** (contrôle pointage) |
| `get_attachment` | Téléchargement d'une pièce |
| `list_clients` | Référentiel clients |
| `list_client_invoices` | Factures clients |
| `list_supplier_invoices` | Factures fournisseurs |

### Outils multi-organisation (⚠️ disponibilité à tester)

`export_transactions` et `export_transaction_attachments` sont documentés comme
disponibles **uniquement sur l'endpoint multi-organisation**
(https://mcp.qonto.com/mcp/organizations/... ). Si indisponibles :

> **Fallback** : utiliser `list_transactions` paginé (via `next_start_page`) et
> déléguer l'export CSV à un script Python local.

## Outils INTERDITS sans validation explicite

- Création / envoi de **facture client**, devis, avoir
- Création de **virement** (SEPA, international, bulk)
- Création / modification de **carte**
- Toute **modification de transaction** (catégorie, label, attachment detach)

Toute tentative d'écriture doit être **annoncée puis stoppée** en attente d'un « oui »
explicite de l'utilisateur.

## Procédure obligatoire — Snapshot horodaté

**AVANT tout calcul ou analyse**, les données récupérées sont sauvegardées localement.

1. **Nommage** : `qonto-exports/{type}_{AAAA-MM}.{ext}`
   - `transactions_2026-06.json` … `transactions_2026-12.json`
   - `balance_2026-11.json`
   - `attachments_2026-06.json`
   - `factures-clients_2026-11.json`
   - `factures-fournisseurs_2026-11.json`
2. **En-tête de snapshot** : tout JSON sauvegardé contient un bloc
   `_meta` : `{ "source": "mcp:qonto", "outil": "list_transactions",
   "extrait_le": "<ISO8601>", "organisation_id": "...", "filtres": {...},
   "nb_enregistrements": N }`
3. **Immutabilité** : un snapshot existant n'est **jamais écrasé**. Une nouvelle
   extraction du même mois produit `transactions_2026-06_v2.json`, `_v3.json`…
4. **Jamais de calcul sur les données « en direct » du MCP** : toujours sur le fichier
   sauvegardé. Le MCP sert à **alimenter**, Python sert à **calculer**.

## Procédure de session type

```
1. Lire memory-bank/suivi-exercice.md  → récupérer le dernier transaction_id traité
2. list_bank_accounts                  → soldes actuels
3. list_transactions (depuis la date du dernier ID traité, statut: completed)
4. list_transaction_attachments        → contrôle de présence des justificatifs
5. Écrire le snapshot dans qonto-exports/ (nommage ci-dessus, _meta en en-tête)
6. Mettre à jour suivi-exercice.md (dernier ID traité, solde rapproché)
7. Seulement ensuite : lancer scripts/ Python sur le snapshot
```

## Contrôles systématiques sur les transactions

| Contrôle | Action si anomalie |
|---|---|
| Statut ≠ `completed` (pending/declined) | **Exclure** du rapprochement, lister à part |
| Aucun justificatif attaché | ⚠️ alerte A2 (règle 01) + TVA non déductible par défaut |
| Contrepartie hors France | ⚠️ alerte A4 / A5 → vérifier TVA intracom |
| Virement vers le Président | ⚠️ surveiller l'origine : remboursement de frais (`455100` **créditeur** ok) vs avance (**débiteur interdit**) |
| Montant > 500 € HT | ⚠️ alerte A8 → vérifier nature charge/immobilisation |

## Sécurité et limites

- L'**OAuth** est réalisé par l'utilisateur : l'agent ne consent jamais à sa place.
- Les tokens sont stockés par VS Code dans le trousseau OS.
- Les URLs de fichiers renvoyées par Qonto (`file_url`, presigned) sont
  **temporaires** et à traiter comme des **mots de passe** : ne jamais les logguer
  en clair dans un fichier versionné.
- **Aucune donnée Qonto ne sort du workspace** vers un service tiers.
