# Mapping Qonto → PCG

> ⚠️ **TABLE PROVISOIRE — À VALIDER LIGNE PAR LIGNE.**
> Ce mapping est une **amorce de travail**, construite à partir des contreparties
> courantes. Aucune ligne n'est « vraie » tant qu'elle n'a pas été confrontée à une
> facture réelle et validée (utilisateur et/ou expert-comptable).
> Statuts : `⚠️ À VALIDER` · `✅ VALIDÉ` · `🔴 INCONNU`

## 1. Colonnes de référence

| Colonne | Signification |
|---|---|
| Contrepartie Qonto | Libellé tel qu'il apparaît dans les transactions |
| Sens | D = encaissement, C = décaissement, DC = les deux |
| Compte PCG | compte de charge/produit |
| Complément | compte de tiers / TVA |
| TVA | taux applicable ou « non déductible » |
| Journal | AC (achats) · VE (ventes) · BQ (banque) · OD (opérations diverses) |
| Statut | niveau de validation |

## 2. Achats et frais généraux

| Contrepartie Qonto | Sens | Compte PCG | Complément | TVA | Journal | Statut |
|---|---|---|---|---|---|---|
| **Qonto** (abonnement) | C | `627800 — Services bancaires et assimilés` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Qonto** (frais de tenue de compte) | C | `627800` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **URSSAF** | C | `431000 — Sécurité sociale` | `401000` | — | AC | ⚠️ À VALIDER |
| **Impôts / DGFiP** | C | `444000 — État, impôts sur les bénéfices` | `401000` | — | AC | ⚠️ À VALIDER |
| **Impôts / DGFiP (CFE)** | C | `635110 — Cotisation foncière des entreprises` | `448600` (à payer) | — | OD | ⚠️ À VALIDER |
| **Domiciliataire** (Vivienne Domiciliation) | C | `613200 — Locations` (ou `622600 Honoraires`) | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Fournisseur SaaS** (France) | C | `611000 — Services extérieurs (abonnements)` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Fournisseur SaaS** (hors UE, ex. US) | C | `611000` | `401000` | **non déductible** | AC | 🔴 INCONNU |
| **Fournisseur SaaS** (UE) | C | `611000` | `401000` + `445200` | **autoliquidation** | AC | 🔴 INCONNU |
| **Coût de matériel / informatique ≤ 500 € HT** | C | `606300 — Fournitures informatiques` (ou `606400`) | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Coût de matériel / informatique > 500 € HT** | C | `218300 — Matériel de bureau et informatique` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Déplacements / transport** | C | `625100 — Voyages et déplacements` | `401000` | 20 % / 10 % | AC | ⚠️ À VALIDER |
| **Restauration** | C | `625700 — Réceptions` (ou `625600`) | `401000` | 20 % / 10 % | AC | ⚠️ À VALIDER |
| **Télécom / Internet** | C | `626000 — Frais postaux et télécommunications` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Loyer / bureau** | C | `613200 — Locations` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Assurance** | C | `616000 — Primes d'assurance` | `401000` | exonérée (souvent) | AC | ⚠️ À VALIDER |
| **Honoraires expert-comptable** | C | `622600 — Honoraires` | `401000` | 20 % | AC | ⚠️ À VALIDER |
| **Formation (achat pour LR Data)** | C | `632400` (ou `631800`) | `401000` | selon nature | AC | ⚠️ À VALIDER |

### 2.1 Contreparties RÉELLES identifiées (snapshot `transactions_2026-06.json`)

| Contrepartie Qonto | Sens | Compte PCG | Complément | TVA | Journal | Statut |
|---|---|---|---|---|---|---|
| **Qonto** (avoir frais, `qonto-credit-note`) | D | `627800 — Services bancaires et assimilés` | `401000` | 20 % (récup.) | AC | ⚠️ À VALIDER |
| **Vincennes M&B Notaires** (`A LR DATA REST DEPOT DE K…`) | D | **`456100 — Associés, apports`** | `512000` | **aucune** | BQ | ✅ **D-12** |
| **Infomaniak** (`infomaniak.com`, hébergement) | C | `611000 — Services extérieurs` | `401000` | 20 % — **justif. manquant (A2)** | AC | ⚠️ À VALIDER |
| **LDLC** (`LDLC.COM`, matériel 429,75 € TTC) | C | `606300 — Fournitures informatiques` (HT ≈ 358,13 € ≤ 500) | `401000` | 20 % — **justif. manquant (A2)** | AC | ⚠️ À VALIDER |
| **Amazon** (`AMZN Mktp FR`) | C | `606300` (à préciser) | `401000` | **à vérifier (A5, vendeur tiers UE ?)** | AC | 🔴 INCONNU |

> ⚠️ **Aucun de ces achats n'a de justificatif attaché** (4/5 transactions, alerte A2) :
> la TVA est **non déductible par défaut** tant que les factures ne sont pas fournies.
> Les montants HT ne sont donc **pas confirmés** (seul le TTC est certain).


## 3. Ventes

| Contrepartie Qonto | Sens | Compte PCG | Complément | TVA | Journal | Statut |
|---|---|---|---|---|---|---|
| **Client — prestation informatique** | D | `706000 — Prestations de services` (ou `706100`) | `411000` + `445710` | **20 %** | VE | ⚠️ À VALIDER |
| **Client — conseil / stratégie digitale** | D | `706000` | `411000` + `445710` | **20 %** | VE | ⚠️ À VALIDER |
| **Client — formation / enseignement** | D | `706700 — Produits des activités annexes` (à confirmer) | `411000` | **exonéré 261-4-4° ?** | VE | 🔴 INCONNU |
| **Client hors UE** | D | `706000` | `411000` | **exonéré (export)** | VE | 🔴 INCONNU |

> ⚠️ **Point critique TVA (Q3)** : LR Data facture **aussi de la formation**.
> Il faut déterminer, **facture par facture**, si l'exonération **art. 261-4-4° CGI**
> s'applique. Avant validation, **ne jamais présumer 20 %** par défaut sur une
> prestation de formation.

## 4. Apports, capital, dirigeant

| Contrepartie Qonto | Sens | Compte PCG | Complément | TVA | Journal | Statut |
|---|---|---|---|---|---|---|
| **Dépôt de capital** | D | `101300 — Capital souscrit appelé versé` | `456100 — Associés, apports` | — | OD | ⚠️ À VALIDER |
| **Capital non appelé** | — | `109000 — Actionnaires, capital souscrit non appelé` | `101300` | — | OD | 🔴 INCONNU |
| **Virement au Président** | C | `455100 — Associé, compte courant` **(CRÉDITEUR)** | `512000` (Qonto) | — | BQ | ⚠️ À VALIDER |
| **Remboursement de frais au Président** | C | `455100` (créditeur) | `512000` | — | BQ | ⚠️ À VALIDER |
| **Virement du Président vers la société** | D | `455100` (créditeur) | `512000` | — | BQ | ⚠️ À VALIDER |

> 🔴 **ALERTE A1 — INTERDIT** : le compte `455100` ne doit **jamais** être **débiteur**
> en SASU (le dirigeant ne peut pas être débiteur de la société : délit d'abus de bien
> social). Tout débit de `455100` est **bloquant** → requalifier en `451000`
> (compte de groupe) ou constater un compte courant créditeur.

## 5. Banque et opérations financières

| Contrepartie Qonto | Sens | Compte PCG | Complément | TVA | Journal | Statut |
|---|---|---|---|---|---|---|
| **Solde Qonto** | DC | `512000 — Banque` | — | — | BQ | ⚠️ À VALIDER |
| **Intérêts sur compte** | D | `768000 — Autres produits financiers` | `512000` | — | BQ | ⚠️ À VALIDER |
| **Frais de carte** | C | `627800` | `401000` | 20 % | AC | ⚠️ À VALIDER |

## 6. Procédure de validation

Pour chaque ligne du mapping :

1. Identifier au moins **une facture réelle** correspondante (snapshot Qonto).
2. Vérifier le **compte PCG exact** et le **taux de TVA** sur le justificatif.
3. Faire passer le statut de `⚠️ À VALIDER` → `✅ VALIDÉ` en indiquant **date + source**.
4. Si plusieurs comptes possibles, créer une **décision** dans `cabinet-doublon.md`.

## 7. Historique

| Date | Modification | Source |
|---|---|---|
| 2026-11-17 | Création du mapping initial (toutes lignes « À VALIDER ») | Réponses utilisateur + PCG |
| 2026-11-19 | Ajout §2.1 : 5 contreparties **réelles** du snapshot 2026-06 (Qonto, notaires, Infomaniak, LDLC, Amazon) | `qonto-exports/transactions_2026-06.json` |
