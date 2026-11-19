# Cabinet — mode doublon

> Cadrage de la relation avec l'expert-comptable (EC) en poste et **journal des
> décisions / écarts**. L'EC reste la **référence légale** jusqu'à validation finale.

## 1. Contexte

| Élément | Valeur |
|---|---|
| EC en poste | **Oui** — un expert-comptable traite actuellement la comptabilité |
| Objectif | **Doubler** la tenue comptable, comparer, puis décider |
| Livrables EC disponibles | **AUCUN pour l'instant** (réponse Q2 = « d ») |
| Sortie du mode doublon | Quand les écarts seront nuls sur ≥ 2 périodes consécutives |

## 2. Périmètre confié / doublé

| Période | Qui traite ? |
|---|---|
| 05/06/2026 → 08/06/2026 | **EC** (immatriculation, apports de constitution) |
| **09/06/2026 → 31/12/2026** | **Doublon** (nous reproduisons) |
| 01/01/2027 → 31/12/2027 | EC uniquement (hors périmètre pour l'instant) |

> ⚠️ **Hypothèse à confirmer** : on suppose que l'EC couvre la période de constitution
> et que le doublon démarre au 09/06/2026 (1re transaction Qonto). À vérifier avec lui.

## 3. Livrables EC attendus (à déposer dans `reference-expert-comptable/`)

| Livrable | Utilité pour le doublon | Reçu ? |
|---|---|---|
| **Balance générale** (par période / annuelle) | Comparaison compte à compte | ❌ |
| **FEC** de l'EC | Comparaison exacte des écritures | ❌ |
| **CA3** déposées | Réconciliation TVA | ❌ |
| **Grand livre** | Analyse des imputations | ❌ |
| **Bilan / compte de résultat** provisoires | Contrôle des agrégats | ❌ |
| **Écritures d'ouverture** (à-nouveaux) | Point de départ du doublon | ❌ |

> 🔒 Ces fichiers ne sont **jamais modifiés**. Le script `comparer_avec_ec.py` les lit
> en lecture seule.

## 4. Méthode de comparaison

Pour chaque période :

1. Générer nos journaux depuis les snapshots Qonto.
2. Calculer notre **balance** par compte (débit, crédit, solde).
3. Charger la balance EC (si disponible).
4. Produire un **rapport d'écarts** :
   - écart par compte (notre solde − solde EC)
   - écritures EC absentes chez nous
   - écritures chez nous absentes chez l'EC
5. Qualifier chaque écart : `imputation différente` · `périmètre` · `omission` ·
   `méthode` (amortissement, TVA, provision) · `erreur`.

## 5. Questions ouvertes à trancher avec l'EC

| # | Question | Impact | Statut |
|---|---|---|---|
| E1 | Confirme-t-il la **clôture du 1er exercice au 31/12/2027** ? | Périmètre, IS proratisé | 🔴 OUVERTE |
| E2 | Le **capital social est-il libéré** ? | IS 15 %, comptes 101300/109000 | ⚠️ PARTIELLE — voir D-05 (hypothèse : non libéré) |
| E3 | Comment a-t-il traité le **matériel passé en charge** ? | Écart de résultat | 🔴 OUVERTE — voir D-09 |
| E4 | Les **factures de formation** sont-elles **exonérées** (261-4-4°) ? | TVA collectée | ⚠️ PARTIELLE — voir D-06 (statu quo TVA 20 %) |
| E5 | Quelle **discipline pour la CFE** (compte, provision) ? | Comptes 635110/448600 | ✅ DÉCIDÉE en interne — voir D-08 (à confronter à l'EC) |
| E6 | Quels **comptes** a-t-il retenus pour les ventes (706000 / 706100 / 706700) ? | Mapping | 🔴 OUVERTE |
| E7 | Fournit-il **balance + FEC** (au format SII) ? | Comparaison | 🔴 OUVERTE |

## 6. Journal des décisions

### D-01 — Posture « doublon prudent »
- **Date** : 2026-11-17
- **Décision** : aucun livrable produit n'est opposable ; l'EC reste la référence.
- **Justification** : l'EC est toujours en poste ; éviter tout risque de double
  comptabilité incohérente.
- **Alternative écartée** : remplacer immédiatement l'EC (risqué sans backtest).
- **À revoir** : oui, à la sortie du mode doublon.

### D-02 — Périmètre démarrant au 09/06/2026
- **Date** : 2026-11-17
- **Décision** : le doublon démarre à la 1re transaction Qonto (09/06/2026).
- **Justification** : la société est immatriculée le 08/06/2026 ; rien avant.
- **Alternative écartée** : démarrer au 05/06/2026 (date d'activité) — pas de flux.
- **À revoir** : non (sauf contradiction de l'EC).

### D-03 — Règle PCG stricte sur les immobilisations
- **Date** : 2026-11-17
- **Décision** : tout bien **> 500 € HT** unitaire est immobilisé et amorti.
- **Justification** : choix utilisateur (Q2 = « b »), conforme au PCG.
- **Alternative écartée** : maintenir le tout-en-charge (choix initial de l'EC ?).
- **À revoir** : oui — **écart probable avec l'EC** à mesurer (cf. E3).

### D-04 — Exercice long et IS proratisé
- **Date** : 2026-11-17
- **Décision** : traiter le 1er exercice comme **long** (09/06/2026 → 31/12/2027).
- **Justification** : Kbis, date de clôture du 1er exercice = **31/12/2027**.
- **Alternative écartée** : clôture au 31/12/2026 (réponse initiale, contredite par le Kbis).
- **À revoir** : oui — à confirmer avec l'EC (E1).

### D-05 — Capital social : hypothèse prudente « non libéré »
- **Date** : 2026-11-18
- **Décision** : statut de libération du capital **introuvable** (Kbis muet, statuts non
  fournis, relevé de constitution non fourni) → hypothèse retenue : **capital NON
  entièrement libéré**. L'IS est **provisionné à 25 %** (taux normal).
- **Justification** : sans preuve de libération intégrale, le taux réduit de 15 % n'est
  pas applicable (condition légale). Prudence = provisionner au taux le plus élevé.
- **Alternative écartée** : provisionner à 15 % (gain d'IS potentiel mais risque de
  rappel si la libération n'est pas démontrée).
- **Action** : rechercher la preuve dans les **statuts** (clause capital) ou le **relevé
  bancaire de constitution** (dépôt avant l'immatriculation du 08/06/2026) ; question E2.
- **À revoir** : oui — dès qu'une preuve est trouvée.

### D-06 — TVA sur les factures de formation : statu quo à 20 %
- **Date** : 2026-11-18
- **Décision** : les factures de formation **déjà émises** portent la TVA à **20 %** →
  on **ne régularise pas** (pas d'avoir). La formation est isolée sur le compte
  **`706700 — Produits des activités annexes`** (suivi séparé) avec **`445710`** en
  collectée. L'alerte « exonération art. 261-4-4° CGI à vérifier » reste active dans
  `calculer_tva.py`.
- **Justification** : le Kbis mentionne « **formation non continue et non qualifiante** »,
  ce qui **éloigne** a priori de l'exonération 261-4-4° (qui vise l'enseignement
  scolaire/universitaire et la formation professionnelle continue). Facturer la TVA est
  donc **défendable** et constitue une **option implicite** (art. 260-1 CGI) qui reste à
  formaliser.
- **Alternative écartée** : considérer les factures comme exonérées → imposerait des
  avoirs et une refacturation, avec un risque accru de redressement.
- **⚠️ Risque résiduel** : si l'EC confirme l'exonération obligatoire, il faudra des
  **avoirs** et une **déclaration d'option** formelle. Question E4.
- **À revoir** : oui — réponse EC indispensable.

### D-07 — Amortissement : convention 33,33 % (3 ans) + prorata en jours
- **Date** : 2026-11-18
- **Décision** : le matériel informatique est amorti en **linéaire sur 3 ans** (taux
  **33,33 %**), avec **prorata temporis en jours** (`jours_détenus / 365`).
- **Justification** : durée d'usage professionnel courante pour du matériel informatique
  (cf. `immobilisations-et-charges.md` §4) ; un « taux moyen » global n'existe pas en PCG,
  on amortit **par bien**.
- **Alternative écartée** : taux unique arbitraire toutes catégories (non conforme au PCG).
- **Mise en œuvre** : `scripts/amortissements.py` (Decimal, prorata en jours, `.meta.json`).
- **À revoir** : non, sauf instruction contraire de l'EC.

### D-08 — CFE : `635110` au débit, `448600` en provision
- **Date** : 2026-11-18
- **Décision** : la CFE est comptabilisée en **`635110 — Cotisation foncière des
  entreprises`** (débit) avec contrepartie **`448600 — État, charges à payer`** (crédit)
  à la clôture ; le règlement solde `448600` par `512000`.
- **Justification** : `444000` est réservé à l'**impôt sur les sociétés** ; le mélanger
  avec la CFE brouille la lecture de l'IS. `635110` est le compte PCG dédié à la CFE.
- **Alternative écartée** : `444000` (compte État impôts sur les bénéfices) — écarté.
- **À revoir** : à confronter à la pratique de l'EC (question E5).

### D-09 — Matériel > 500 € HT : reclassement en immobilisation
- **Date** : 2026-11-18
- **Décision** : le matériel **> 500 € HT** unitaire passé en charge sera **reclassé** en
  `218300 — Matériel de bureau et informatique` au **31/12/2026**, puis amorti
  (`681100` / `281830`) selon D-07.
- **Justification** : choix utilisateur (Q2 = « b », règle PCG stricte).
- **Alternative écartée** : statu quo (tout en charge) — écarté par décision utilisateur.
- **⚠️ Prérequis** : le reclassement exige le **libellé du bien, le montant HT, la date
  d'achat et le n° de facture**. Tant que ces données ne sont pas extraites de Qonto, le
  registre reste vide et **aucune écriture n'est produite** (option B retenue).
- **À revoir** : oui — écart probable avec l'EC (E3).
### D-10 — Documentation : préfixe `docs` et garde-fou README (B3)
- **Date** : 2026-11-19
- **Décision** :
  1. le préfixe de branche **`docs`** est ajouté aux préfixes autorisés par
     `scripts/creer_branche.sh` (`feat` · `fix` · `chore` · `docs`) pour les tâches
     purement documentaires ;
  2. la **mise à jour du `README.md` devient obligatoire dans le même commit** que tout
     changement d'arborescence / de scripts / d'entry points — règle **`.clinerules/08`** ;
  3. application outillée **B3** : hook pre-commit `readme-a-jour` **avertisseur
     non bloquant** (contournable par `SKIP=readme-a-jour`) ;
  4. le projet est **packagé** (`[build-system]` hatchling + `[tool.uv] package = true`)
     afin que les entry points `[project.scripts]` **fonctionnent réellement** — ils
     étaient déclarés depuis l'origine mais **ignorés par uv** (`uv run equilibre`
     échouait avant correction). Aucune dépendance runtime n'est ajoutée.
- **Justification** : le README était réduit à deux lignes ; un harnais documenté doit
  décrire son interface, et la doc doit rester **atomique** avec le changement de source
  (règle R4/07). Le projet a déjà une culture de garde-fous pre-commit `repo: local`, en
  stdlib pure — l'avertisseur s'y insère sans friction ni téléchargement réseau.
- **Alternative écartée** :
  - garde-fou **bloquant** (B2) : trop rigide, génère des échecs sur des commits légitimes
    qui touchent `memory-bank/` sans changer le README ;
  - simple règle documentaire (B1) seule : insuffisante, aucun rappel automatique.
- **⚠️ Défaut constaté (lecture seule, non corrigé ici)** :
  `scripts/amortissements.py` est un **module bibliothèque** — il **n'expose pas de
  fonction `main`** et **ne possède aucune CLI**, alors que sa **docstring décrit** une
  interface (`--registre`, `--sortie`, `--exercice`, `--json`, codes de sortie
  `0/1/2/3`) et un livrable `journal_OD_amortissements_<exercice>.csv` qui **n'existent
  pas**. En conséquence :
  - **aucun entry point `amortissements`** n'est déclaré dans `pyproject.toml`
    (la tentative `uv run amortissements` échouait sur `ImportError: cannot import name
    'main'`) ;
  - le **registre** d'immobilisations (`immobilisations-et-charges.md` §3) reste vide et
    **aucune écriture OD n'est produite** — cohérent avec l'option B retenue le
    2026-11-18 ;
  - l'écart entre la docstring et le code est **documenté** (README §4.4) mais **non
    corrigé** : décision à prendre (écrire la CLI, ou corriger la docstring).
- **À revoir** : décision à prendre sur `amortissements.py` (CLI vs docstring).




## 7. Table des écarts (à remplir)

| Écart | Période | Compte | Notre valeur | Valeur EC | Delta | Qualification | Action |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

## 8. Historique

| Date | Modification | Source |
|---|---|---|
| 2026-11-17 | Création — 7 questions ouvertes, 4 décisions initiales | Réponses utilisateur + Kbis |
| 2026-11-19 | **D-10** — documentation : préfixe `docs`, garde-fou README (B3), packaging des entry points ; défaut `amortissements.py` consigné | Validé par l'utilisateur |
