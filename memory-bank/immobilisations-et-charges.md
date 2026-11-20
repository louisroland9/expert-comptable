# Immobilisations et charges — LR Data

> Suivi des acquisitions et de leur traitement comptable. **Règle retenue : PCG stricte**
> (tout bien **> 500 € HT** unitaire = immobilisation).

## 1. Règle de tri

| Montant HT unitaire | Traitement | Compte |
|---|---|---|
| **≤ 500 €** | Charge de l'exercice | `606300` / `606400` |
| **> 500 €** | Immobilisation amortissable | `218300` (+ `281830`) |

> ⚠️ Le seuil s'apprécie **par bien**, et non par facture (si une facture contient
> 3 écrans à 400 €, on reste en charge).

## 2. Situation connue à ce jour

| Élément | Information | Statut |
|---|---|---|
| Matériel acquis et **passé en charge** | **Oui** (confirmé par l'utilisateur) | ✅ |
| Nature du matériel | ⚠️ Non précisé | 🔴 À PRÉCISER |
| Montant HT unitaire | ⚠️ Non précisé | 🔴 À PRÉCISER |
| Date d'acquisition | ⚠️ Non précisée | 🔴 À PRÉCISER |
| Traitement EC | ⚠️ Inconnu (probablement en charge) | 🔴 À CONFIRMER |

> **Constat** : le matériel a été **initialement passé en charge**. Cela peut être :
> - du **petit matériel** (≤ 500 € HT) → **conforme**, rien à faire ;
> - du **matériel > 500 € HT** → **à reclasser** en immobilisation (écart probable avec l'EC).

## 3. Registre des immobilisations

> **Convention retenue (D-07)** : amortissement **linéaire**, durée **3 ans** (taux
> **33,33 %**) pour le matériel informatique, **prorata temporis en jours**
> (`jours_détenus / 365`). Calcul par `scripts/amortissements.py` — jamais de tête.

| # | Date | Libellé | Fournisseur | Facture | HT | TVA | Durée | Dotation 2026 | Compte | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — |

> **Registre vide** : aucune donnée matériel n'a encore été extraite de Qonto
> (option B retenue le 2026-11-18). À alimenter depuis les snapshots Qonto
> (transactions catégorisées en fournitures/matériel) + les justificatifs, puis
> exécuter `python3 scripts/amortissements.py --registre memory-bank/immobilisations-et-charges.md`.
>
> Le script **ne produit aucune écriture** tant que le registre est vide : il sort
> avec le code `1` (avertissement) et l'indique explicitement.

## 4. Durées d'amortissement usuelles (linéaire)

| Type de bien | Durée | Compte d'amortissement |
|---|---|---|
| Matériel informatique (PC, écrans) | **3 ans** | `281830` |
| Serveur / matériel réseau | 3 à 5 ans | `281830` |
| Mobilier de bureau | 5 à 10 ans | `281840` |
| Logiciels | 1 à 3 ans | `280500` |
| Matériel de téléphonie | 3 ans | `281830` |

> ⚠️ **Prorata temporis** obligatoire pour l'année d'acquisition (en jours ou en mois,
> selon la convention retenue — à harmoniser avec l'EC).

## 5. Écritures de régularisation (à n'appliquer qu'après validation)

### 5.a Reclassement de la charge vers l'immobilisation

```
Journal : OD   Date : 31/12/AAAA
Libellé : Reclassement {libellé du bien} — facture {n°}
  Débit  218300 — Matériel de bureau et informatique        {HT}
  Crédit 606300 — Fournitures informatiques                 {HT}
```
Contrôle : Σ Débit = Σ Crédit = {HT}

### 5.b Dotation aux amortissements (prorata temporis)

```
Journal : OD   Date : 31/12/AAAA
Libellé : Dotation aux amortissements {libellé} — {année}
  Débit  681100 — Dotations aux amortissements              {annuité}
  Crédit 281830 — Amort. matériel de bureau/informatique    {annuité}
```
Avec : `annuité = HT / durée_années × (jours_détenus / 365)`

> ⚠️ **Ces écritures nécessitent une validation explicite** de l'utilisateur
> (cf. `docs/procedures/01-persona-sasu.md` — interdiction de reclasser sans validation).

## 6. Impact sur le résultat (exercice 2026)

| Scénario | Charge 2026 | Dotation 2026 | Résultat 2026 |
|---|---|---|---|
| Statu quo (matériel en charge) | {HT} | 0 | plus faible |
| Reclassement (immobilisation) | 0 | {HT × prorata} | plus élevé |

> L'écart de résultat **modifie l'IS** : à chiffrer précisément avec Python
> (jamais de tête — cf. `docs/procedures/03-regles-calculs-python.md`).

## 7. Procédure

1. Extraire les transactions Qonto (snapshot) et **filtrer** les achats de matériel.
2. Récupérer les **justificatifs** (`list_transaction_attachments`) → montant HT unitaire.
3. Appliquer le **seuil de 500 €** par bien.
4. Renseigner le **registre** (section 3).
5. **Demander validation** avant toute écriture de régularisation.
6. Générer les écritures via un script Python (pas de saisie manuelle des montants).

## 8. Historique

| Date | Modification | Source |
|---|---|---|
| 2026-11-17 | Création — règle PCG stricte retenue, matériel en charge signalé | Réponses utilisateur |
