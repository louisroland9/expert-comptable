# Identité de la SASU — LR Data

> **Source principale** : Extrait Kbis — Greffe du Tribunal des Activités Économiques
> de Paris, à jour au **08/06/2026**. Statut : ✅ VALIDÉ (sauf mention contraire).

## Identification

| Élément | Valeur | Statut |
|---|---|---|
| Dénomination sociale | **LR Data** | ✅ |
| Forme juridique | **SASU** — Société par actions simplifiée à associé unique | ✅ |
| N° RCS | **105 991 475** R.C.S. Paris | ✅ |
| N° de gestion | 2026B28790 | ✅ |
| **SIREN** | **105 991 475** | ✅ |
| **EUID** | **FR7501.105991475** | ✅ |
| **N° TVA intracommunautaire** | **FR95105991475** | ✅ |
| Date d'immatriculation | **08/06/2026** | ✅ |
| Date de commencement d'activité | **05/06/2026** | ✅ |
| Durée de la personne morale | jusqu'au **07/06/2125** | ✅ |
| Origine | Création | ✅ |
| Mode d'exploitation | Exploitation directe | ✅ |

## Capital social

| Élément | Valeur | Statut |
|---|---|---|
| Capital social | **1 000,00 €** | ✅ (Kbis) |
| **Capital entièrement libéré ?** | **NON — hypothèse prudente** (info introuvable) | ⚠️ **À CONFIRMER** (D-05) |
| Montant libéré | — (hypothèse : 0 € appelé) | ⚠️ **À CONFIRMER** |
| Compte à utiliser si non libéré | `101300` (appelé versé) + `109000` (non appelé) | — |

> 🔎 **Élément de preuve (2026-11-19)** : le snapshot `transactions_2026-06.json` contient
> un virement de **1 000,00 €** reçu le **10/06/2026** du notaire (*Vincennes M&B
> Notaires*), libellé `A LR DATA REST DEPOT DE K…` = « reste dépôt de capital ».
> ⚠️ Ce flux **ne prouve PAS** une libération intégrale : le mot « **RESTE** » implique un
> versement **antérieur** (probablement chez le notaire, hors périmètre). Traitement
> comptable : apport en capital `456100` (cf. **D-12**). L'hypothèse « non libéré »
> (**D-05**) et l'IS à 25 % **restent en vigueur** jusqu'à production des statuts ou de
> l'attestation notariale (**question E2**).

> ⚠️ **Le Kbis ne mentionne pas le statut de libération du capital.** À vérifier dans :
> 1. les **statuts** (clause capital : « libéré » / « à libérer dans les 5 ans ») ;
> 2. le **relevé bancaire de constitution** (dépôt de capital avant immatriculation) ;
> 3. une **attestation du domiciliataire** ou du notaire.
>
> Impact : condition du **taux réduit d'IS à 15 %** (capital entièrement libéré exigé)
> et choix des comptes `101300` / `109000`.

## Siège et domiciliation

| Élément | Valeur |
|---|---|
| Adresse du siège | **47 rue Vivienne, 75002 Paris** |
| Domiciliataire | **Vivienne Domiciliation** (RCS 994 567 121) |

## Activités déclarées (Kbis)

1. **Le conseil en informatique, en programmation et en stratégie digitale**, ainsi que
   la réalisation de prestations associées.
2. **Enseignement privé** dans les 1er, 2e et 3e cycles de l'enseignement supérieur.
3. **Formation non continue et non qualifiante**, en ligne et en présentiel, dans le
   domaine de l'informatique, du Cloud & du développement.
4. **Conception et développement de logiciels et outils informatiques**, exploitation
   et maintenance.

> ⚠️ **Impact TVA majeur** : l'activité de **formation / enseignement** peut relever de
> l'**exonération art. 261-4-4° CGI**. Vérifier avec l'EC quelles factures sont
> exonérées et lesquelles supportent la TVA à 20 %. Cf. `docs/procedures/04-cycle-fiscal-sasu.md`.

## Direction

| Élément | Valeur |
|---|---|
| Président | **Roland Louis Marc** |
| Né le | 30/05/1995 à Reims (51) |
| Nationalité | Française |
| Rémunération prévue | **0 €** (confirmé) |
| Dividendes prévus | **0 €** (confirmé) |

## Exercice comptable

| Élément | Valeur |
|---|---|
| Date de clôture (statuts) | **31 décembre** |
| **Clôture du 1er exercice social** | **31/12/2027** ⚠️ (exercice long, ~19 mois) |
| Début effectif | **05–09/06/2026** |
| **Périmètre du doublon** | **09/06/2026 → 31/12/2026** |

> ⚠️ Le **1er exercice est long** (immatriculation 08/06/2026 → 31/12/2027). Le seuil
> de l'IS à taux réduit (42 500 €) est **proratisé** sur la durée de l'exercice.

## Régime fiscal

| Élément | Valeur |
|---|---|
| TVA | **Régime réel normal — CA3 mensuelle** |
| IS | Taux normal 25 % · taux réduit 15 % sous conditions (⚠️ capital libéré ?) |

> ⚠️ **Hypothèse de provisionnement retenue (D-05)** : le statut de libération du capital
> étant introuvable, l'IS est **provisionné à 25 %** (hypothèse prudente). Le taux réduit
> de 15 % ne sera appliqué qu'après preuve de libération intégrale (statuts / relevé de
> constitution / balance EC).
| CFE | **Due** |
| Exercice doublon | 09/06/2026 → 31/12/2026 |

## Outils et organismes

| Élément | Valeur |
|---|---|
| Banque | **Qonto** (1re transaction : 09/06/2026) |
| Serveur MCP | `qonto` — `https://mcp.qonto.com/mcp` |
| Télétransmission liasse | **Espace professionnel impots.gouv.fr** |
| Expert-comptable | **En poste** (référence légale — mode doublon) |
| Plateforme e-invoicing | **Qonto** (Plateforme Agréée certifiée) |

## Historique des mises à jour

| Date | Modification | Source |
|---|---|---|
| 2026-11-17 | Création du fichier depuis le Kbis | Kbis 08/06/2026 + réponses utilisateur |
