# e-invoicing — état de conformité LR Data

> Suivi de la réforme de la **facturation électronique**. Cadre détaillé dans
> `.clinerules/06-e-invoicing.md`.

## 1. Calendrier applicable à LR Data

| Jalon | Obligation | Concerné ? | Statut |
|---|---|---|---|
| **01/09/2026** | **Réception** de factures électroniques (Plateforme Agréée) | **OUI** | ⚠️ À VÉRIFIER |
| **01/09/2026** | Émission (GE / ETI) | non | — |
| **01/09/2027** | **Émission** (PME / TPE) → **LR Data** | **OUI** | 🔴 À PRÉPARER |

> ⚠️ Depuis le 01/09/2026, LR Data doit être **en capacité de recevoir** des factures
> électroniques via une Plateforme Agréée. À vérifier au plus vite.

## 2. Choix de la plateforme

| Élément | Valeur | Statut |
|---|---|---|
| Plateforme Agréée retenue | **Qonto** (certifiée) | ⚠️ À CONFIRMER |
| Compte Qonto activé pour l'e-invoicing | ? | 🔴 À VÉRIFIER |
| Inscription à l'annuaire national | ? | 🔴 À FAIRE |
| SIREN publié | 105 991 475 | ✅ |

## 3. Conformité des flux

### 3.1 Factures émises (clients)

| Mois | Nb factures | Format | Conformes | Non conformes | Observations |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### 3.2 Factures reçues (fournisseurs)

| Mois | Nb factures | Via PA | PDF simple | Papier | Sans justificatif |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## 4. Mentions obligatoires à contrôler

- [ ] Numérotation séquentielle continue
- [ ] Date d'émission + date de prestation
- [ ] **SIREN 105 991 475** + **TVA FR95105991475** de LR Data
- [ ] Identité complète du client (nom, adresse, SIREN/SIRET)
- [ ] Détail des prestations (désignation, quantité, PU HT)
- [ ] Taux et montant de **TVA par taux**
- [ ] Totaux **HT / TVA / TTC**
- [ ] **Mention exonération** « TVA non applicable, art. 261-4-4° CGI » pour la formation
- [ ] Conditions de règlement, pénalités, indemnité forfaitaire 40 €
- [ ] **Format Factur-X** (PDF/A-3 + XML CII) si émission dématérialisée

## 5. Points de vigilance

| # | Point | Impact |
|---|---|---|
| V1 | La **formation exonérée** doit porter la mention légale d'exonération | Rejet / requalification TVA |
| V2 | Les factures clients doivent être **rattachées** aux encaissements Qonto | Pointage / FEC |
| V3 | Un justificatif **PDF simple** n'est pas un Factur-X | Non-conformité |
| V4 | L'**annuaire** doit connaître les clients destinataires | Blocage d'émission |

## 6. Plan d'action

| # | Action | Responsable | Échéance | Statut |
|---|---|---|---|---|
| 1 | Vérifier l'activation e-invoicing Qonto | Utilisateur | ASAP | 🔴 |
| 2 | Confirmer l'inscription à l'annuaire | Utilisateur | ASAP | 🔴 |
| 3 | Basculer les fournisseurs en réception PA | Utilisateur | ASAP | 🔴 |
| 4 | Mettre en place l'archivage local (PDF + XML) | Agent | à planifier | 🔴 |
| 5 | Écrire `scripts/verifier_facturx.py` (contrôle) | Agent | à planifier | 🔴 |
| 6 | Valider la conformité de l'émission avant 01/09/2027 | Utilisateur + EC | 2027 | 🔴 |

## 7. Historique

| Date | Modification | Source |
|---|---|---|
| 2026-11-17 | Création — cadre réforme 2024, jalons 09/2026 et 09/2027 | impots.gouv.fr + docs Qonto |
