# 06 — e-invoicing (facturation électronique)

## Cadre

- 🇫🇷 Réforme française de la **facturation électronique** (*e-invoicing*) et du
  **e-reporting**, issue de la loi de finances 2024.
- La généralisation passe par des **Plateformes Agréées** (PA, ex-PDP), seules
  habilitées à émettre / transmettre / recevoir les factures dématérialisées.
- Format pivot : **Factur-X** (PDF/A-3 + XML **CII** conforme **EN 16931**),
  ou UBL ; données de facturation structurées obligatoires.
- **Annuaire national** des destinataires / émetteurs.

## Calendrier (à date)

| Jalon | Obligation |
|---|---|
| **01/09/2026** | **Réception** obligatoire pour **toutes** les entreprises ; **émission** pour GE et ETI |
| **01/09/2027** | **Émission** obligatoire pour **PME / TPE** (dont LR Data) |

> ⚠️ **LR Data est une TPE** : l'émission en Factur-X devient obligatoire au
> **01/09/2027**. Sécuriser la mise en conformité **courant 2027**.

## Canal retenu

**Qonto** est une **Plateforme Agréée certifiée** → canal naturel pour LR Data.

| Sujet | Décision |
|---|---|
| Plateforme d'émission | **Qonto** (à confirmer) |
| Plateforme de réception | **Qonto** |
| Format | **Factur-X** |
| Annuaire | inscription requise (statut ⚠️ À FAIRE) |

## Règles pour l'agent

### R1 — Distinguer émission et réception

- **Réception** : les factures fournisseurs arrivent via la PA → elles doivent être
  **rattachées** à une transaction Qonto (pointage) et servir de **justificatif**.
- **Émission** : les factures clients partent via la PA → une copie (PDF + XML) est
  archivée localement dans `qonto-exports/` ou un dossier d'archive dédié.

### R2 — Contrôle avant tout FEC / clôture

Avant de générer un FEC ou de clôturer un mois :

1. Vérifier que **chaque transaction** de vente a une **facture client** e-invoicing.
2. Vérifier que **chaque achat professionnel** a un **justificatif** rattaché.
3. Lister les **non-conformes** (justificatif papier, PDF simple sans XML, absence de
   justificatif) → ces lignes sont alimentées dans `memory-bank/e-invoicing.md`.

### R3 — Mentions obligatoires (Factur-X)

L'agent vérifie au minimum :

- Numérotation séquentielle, date d'émission, date de la prestation
- **SIREN** (ou SIRET) **105 991 475** et **n° TVA FR95105991475** de LR Data
- Identité complète du client (SIREN/SIRET, adresse)
- Détail des prestations, **quantités, prix unitaires HT**, taux de TVA
- **Total HT**, **TVA** par taux, **total TTC**
- Mentions particulières :
  - **« TVA non applicable, art. 261-4-4° CGI »** pour la **formation exonérée** ⚠️
  - « Autoliquidation » pour les achats UE (côté fournisseur)
  - Conditions de règlement, pénalités de retard, indemnité forfaitaire 40 €
- Précision sur l'**exonération** éventuelle (formation) et son fondement légal

### R4 — Interdictions

- ❌ Générer un Factur-X « maison » pour un **usage de production** : le format
  (PDF/A-3 + XML CII) est complexe ; **on s'appuie sur Qonto**, pas sur un script.
- ❌ Émettre une facture client via le MCP Qonto **sans validation explicite**.
- ❌ Marquer un fournisseur comme conforme sans justificatif présent.

### R5 — Périmètre des scripts

`scripts/verifier_facturx.py` est un **outil de contrôle** (lecture) :

- présence d'un fichier **PDF/A-3** et d'une **pièce jointe XML** (`factur-x.xml`)
- présence des champs clés (SIREN, TVA, totaux)
- cohérence HT + TVA = TTC

Il **ne génère pas** de Factur-X.

## Suivi

L'état de la mise en conformité est tenu dans `memory-bank/e-invoicing.md`
(onboarding PA, inscription annuaire, fournisseurs/clients conformes, jalons).
