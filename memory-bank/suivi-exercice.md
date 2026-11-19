# Suivi de l'exercice — LR Data

> Tableau de bord de l'avancement. **À mettre à jour après chaque extraction Qonto ou
> clôture mensuelle** (cf. `.clinerules/05-protocole-memoire.md`).

## Paramètres de l'exercice

| Élément | Valeur |
|---|---|
| Exercice social (statuts) | **09/06/2026 → 31/12/2027** (exercice long) |
| **Périmètre suivi ici** | **09/06/2026 → 31/12/2026** |
| Régime TVA | Réel normal — **CA3 mensuelle** |
| Compte bancaire | Qonto (`512000`) — 1re transaction **09/06/2026** |

## État des snapshots Qonto

| Snapshot | Type | Date d'extraction | Nb lignes | Dernier `transaction_id` | Statut |
|---|---|---|---|---|---|
| — | — | — | — | — | ⏳ en attente |

> Nommage : `qonto-exports/{type}_{AAAA-MM}.json` (cf. `.clinerules/02`).
> Un snapshot existant n'est **jamais écrasé**.

## Avancement mensuel

| Mois | Snapshot | Transactions pointées | Justificatifs manquants | Réconcilié | CA3 déposée | Validé EC | Écart |
|---|---|---|---|---|---|---|---|
| 2026-06 (09→30) | ⏳ | — | — | — | — | — | — |
| 2026-07 | ⏳ | — | — | — | — | — | — |
| 2026-08 | ⏳ | — | — | — | — | — | — |
| 2026-09 | ⏳ | — | — | — | — | — | — |
| 2026-10 | ⏳ | — | — | — | — | — | — |
| 2026-11 | ⏳ | — | — | — | — | — | — |
| 2026-12 | ⏳ | — | — | — | — | — | — |

Légende : ⏳ à faire · 🔄 en cours · ✅ fait · ⚠️ anomalie

## Rappel des obligations périodiques

| Échéance | Obligation | État |
|---|---|---|
| 15 ou 24 du mois suivant | **CA3** TVA | — |
| 31/12/2026 | Paiement **CFE** (selon avis) | — |
| 15/03/2027 | 1er acompte IS (si concerné) | — |
| ≤ 30/06/2028 | AG d'approbation (6 mois après clôture 31/12/2027) | — |
| 01/09/2027 | **Emission e-invoicing obligatoire (TPE)** | — |

## Suivi de la TVA

| Mois | TVA collectée (20 %) | TVA collectée (exonéré 261-4-4°) | TVA déductible | TVA intracom | Crédit / à payer | CA3 déposée le |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

## Questions ouvertes en cours

| # | Question | Impact | Statut |
|---|---|---|---|
| Q1 | Capital social libéré ou non ? | IS 15 % / comptes 101300-109000 | ⚠️ DÉCIDÉE — hypothèse « non libéré », IS à 25 % (D-05) |
| Q2 | Factures de formation exonérées 261-4-4° ? | TVA collectée | ⚠️ DÉCIDÉE — statu quo TVA 20 % (D-06) |
| Q3 | Taux et durée d'amortissement du matériel ? | Régularisation clôture | ✅ DÉCIDÉE — 33,33 % / 3 ans, prorata jours (D-07) |
| Q4 | Discipline de comptabilisation de la CFE ? | Compte `635110` / `448600` | ✅ DÉCIDÉE — `635110` / `448600` (D-08) |

> Détail et justification de chaque décision : `memory-bank/cabinet-doublon.md` §6 (D-05 à D-09).
> Les points Q1 et Q2 restent **à confirmer par l'EC** (questions E2 et E4).

## Historique

| Date | Événement |
|---|---|
| 2026-11-17 | Création du tableau de bord — aucun snapshot Qonto encore extrait |
