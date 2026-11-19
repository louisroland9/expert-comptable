# Plan comptable — LR Data (SASU)

> Plan de comptes **minimal** réellement retenu pour le dossier, selon le **PCG**
> (Règlement ANC 2014-03). Il est **restrictif** : on n'ajoute un compte que lorsqu'il
> est effectivement utilisé. Tout ajout est justifié et daté.

## Classe 1 — Capitaux propres

| Compte | Intitulé | Usage |
|---|---|---|
| `101300` | Capital souscrit, appelé, versé | Apport initial (1 000 €) — ⚠️ libération à confirmer |
| `109000` | Actionnaires : capital souscrit non appelé | Si capital non intégralement libéré |
| `110000` | Report à nouveau (créditeur) | Résultats antérieurs bénéficiaires |
| `119000` | Report à nouveau (débiteur) | Résultats antérieurs déficitaires |
| `106100` | Réserve légale | Dotations cumulées (10 % du capital = 100 €) |
| `120000` | Résultat de l'exercice (bénéfice) | À la clôture |
| `129000` | Résultat de l'exercice (perte) | À la clôture |

## Classe 2 — Immobilisations

| Compte | Intitulé | Usage |
|---|---|---|
| `218300` | Matériel de bureau et matériel informatique | Biens **> 500 € HT** (règle PCG stricte) |
| `218100` | Installations générales, agencements | Si nécessaire |
| `205000` | Logiciels / concessions | Acquisitions de licences perpétuelles |
| `281830` | Amortissements — matériel de bureau et informatique | Amortissement cumulé (3 ans linéaire par défaut) |
| `280500` | Amortissements — logiciels | 1 à 3 ans |

## Classe 4 — Tiers

| Compte | Intitulé | Usage |
|---|---|---|
| `401000` | Fournisseurs | Achats non réglés |
| `411000` | Clients | Ventes non encaissées |
| `421000` | Personnel — rémunérations dues | **Non utilisé (rémunération 0 €)** |
| `431000` | Sécurité sociale | URSSAF |
| `444000` | État : impôts sur les bénéfices | IS, acomptes |
| `445200` | TVA intracommunautaire (déductible et collectée) | Autoliquidation UE |
| `445660` | TVA déductible sur autres biens et services | Achats France |
| `445710` | TVA collectée | Ventes à 20 % |
| `447000` | Autres impôts, taxes et versements assimilés | Divers |
| `448600` | État, charges à payer | Provision CFE notamment |
| `455100` | Associé — compte courant | **⚠️ CRÉDITEUR uniquement (interdit débiteur)** |
| `456100` | Associés — apports | Dépôt de capital |
| `457000` | Associés — dividendes à payer | **Non utilisé (aucune distribution)** |
| `471000` | Comptes d'attente | À solder impérativement en fin de période |
| `468600` | Charges à payer | Inventaire |

## Classe 5 — Financier

| Compte | Intitulé | Usage |
|---|---|---|
| `512000` | Banque | **Compte Qonto** |

## Classe 6 — Charges

| Compte | Intitulé | Usage |
|---|---|---|
| `606300` | Fournitures informatiques | Petit matériel **≤ 500 € HT** |
| `606400` | Fournitures administratives | Consommables |
| `611000` | Services extérieurs — abonnements | SaaS, hébergement |
| `613200` | Locations | Domiciliation, loyers |
| `615000` | Entretien et réparations | Maintenance |
| `616000` | Primes d'assurance | RC pro, etc. |
| `622600` | Honoraires | Expert-comptable, avocat |
| `625100` | Voyages et déplacements | Transport |
| `625700` | Réceptions | Repas professionnels |
| `626000` | Frais postaux et télécommunications | Téléphone, Internet |
| `627800` | Services bancaires et assimilés | **Qonto** |
| `631800` | Autres charges sociales | Si applicable |
| `635110` | Cotisation foncière des entreprises | **CFE** |
| `641000` | Rémunérations du personnel | **Non utilisé (0 €)** |
| `681100` | Dotations aux amortissements | Immobilisations |

## Classe 7 — Produits

| Compte | Intitulé | Usage |
|---|---|---|
| `706000` | Prestations de services | **Conseil / développement informatique — TVA 20 %** |
| `706100` | Services vendus (alternatif) | À arbitrer avec `706000` |
| `706700` | Produits des activités annexes | **Formation** — ⚠️ exonération 261-4-4° à confirmer |
| `768000` | Autres produits financiers | Intérêts Qonto |

## Journaux retenus

| Code | Journal | Contenu |
|---|---|---|
| `AC` | Achats | Factures fournisseurs |
| `VE` | Ventes | Factures clients |
| `BQ` | Banque | Flux Qonto (virements, cartes, prélèvements) |
| `OD` | Opérations diverses | Inventaire, régularisations, reclassements |
| `AN` | À-nouveaux | Bilan d'entrée (si nécessaire) |

## Règle d'enrichissement

Un compte n'est ajouté que si :
1. il est **utilisé** au moins une fois, **et**
2. son intitulé exact est repris du **PCG**, **et**
3. l'ajout est **daté et justifié** dans l'historique ci-dessous.

## Historique

| Date | Compte | Motif | Source |
|---|---|---|---|
| 2026-11-17 | Plan initial | Création du plan minimal selon PCG 2025/2026 | Réponses utilisateur + Kbis |
