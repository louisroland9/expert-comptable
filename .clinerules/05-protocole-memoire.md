# 05 — Protocole mémoire

## Objectif

`memory-bank/` est la **mémoire persistante** du dossier LR Data. Elle est la source de
vérité entre deux sessions : elle évite de redemander les mêmes informations et de
reproduire des erreurs déjà tranchées.

## R1 — Lecture obligatoire en début de session

**Au tout début de chaque session**, avant toute réponse ou action, lire :

1. `memory-bank/identite-sasu.md` — fiche juridique et fiscale
2. `memory-bank/suivi-exercice.md` — état d'avancement + dernier ID Qonto traité
3. `memory-bank/mapping-qonto-pcg.md` — mapping contrepartie → compte PCG
4. `memory-bank/plan-comptable-sasu.md` — plan de comptes retenu
5. `memory-bank/cabinet-doublon.md` — questions ouvertes / écarts avec l'EC
6. `memory-bank/e-invoicing.md` — état de conformité
7. `memory-bank/immobilisations-et-charges.md` — suivi du matériel

Puis, si des livrables EC ont été déposés : lister `reference-expert-comptable/`.

> Si un fichier est **absent**, le signaler et **ne pas l'inventer** : proposer de le créer.

## R2 — Mise à jour obligatoire

Mettre à jour la mémoire **immédiatement** après :

| Événement | Fichier(s) à mettre à jour |
|---|---|
| Extraction Qonto (snapshot) | `suivi-exercice.md` (dernier ID traité, date de snapshot) |
| Clôture mensuelle | `suivi-exercice.md` (TVA déclarée, solde rapproché) |
| Nouvelle contrepartie identifiée | `mapping-qonto-pcg.md` |
| Nouveau compte PCG utilisé | `plan-comptable-sasu.md` |
| Décision / arbitrage | `cabinet-doublon.md` (journal des décisions) |
| Écart constaté avec l'EC | `cabinet-doublon.md` (table des écarts) |
| Achat > 500 € HT | `immobilisations-et-charges.md` |
| Jalon e-invoicing | `e-invoicing.md` |
| Changement de paramètre juridique/fiscal | `identite-sasu.md` |

## R3 — Format des entrées

- **Datation systématique** : toute mise à jour est horodatée (`AAAA-MM-JJ`).
- **Traçabilité de la source** : préciser d'où vient l'information
  (`Kbis 08/06/2026`, `snapshot Qonto 2026-11`, `validé par l'utilisateur`, `EC`).
- **Statut explicite** : `✅ VALIDÉ` · `⚠️ À CONFIRMER` · `🔴 INCONNU`.
- **Jamais de suppression** : une information périmée est **barrée** ou déplacée en
  historique, jamais effacée (piste d'audit).

## R4 — Ce qui ne va PAS dans la mémoire

- ❌ Données brutes Qonto (elles restent dans `qonto-exports/`)
- ❌ Livrables fiscaux (ils vont dans `exports-fiscaux/`)
- ❌ Secrets, tokens, identifiants (cf. `.gitignore`)
- ❌ Notes de travail temporaires (utiliser `_travail/` et supprimer après usage)

## R5 — Fin de session

Avant de terminer une session, vérifier :

- [ ] Le dernier ID de transaction Qonto traité est enregistré
- [ ] Les snapshots créés sont listés dans `suivi-exercice.md`
- [ ] Les questions ouvertes sont remontées dans `cabinet-doublon.md`
- [ ] Aucun fichier de `qonto-exports/` ou `reference-expert-comptable/` n'a été modifié
- [ ] Les scripts exécutés ont produit un `.meta.json` dans `exports-fiscaux/`

## R6 — Journal des décisions

Toute décision structurante (choix de compte, régime TVA, méthode d'amortissement,
traitement d'un cas limite) est consignée dans `cabinet-doublon.md` au format :

```
### D-{NN} — {titre court}
- Date : AAAA-MM-JJ
- Décision : ...
- Justification : ...
- Alternative écartée : ...
- À revoir : oui/non
```
