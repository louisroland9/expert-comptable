# 04 — Cycle fiscal SASU

## 1. Identification fiscale

| Élément | Valeur |
|---|---|
| Raison sociale | **LR Data** — SASU (associé unique) |
| SIREN / RCS | **105 991 475** R.C.S. Paris |
| EUID | **FR7501.105991475** |
| N° TVA intracommunautaire | **FR95105991475** |
| Siège | 47 rue Vivienne, 75002 Paris |
| Président | Roland Louis Marc |
| Activité | Conseil informatique, programmation, stratégie digitale · **enseignement / formation** · conception & maintenance logicielle |
| Début d'activité | **05/06/2026** |
| Immatriculation | **08/06/2026** |
| 1er exercice | **09/06/2026 → 31/12/2027** (exercice long) |
| Périmètre doublon | **09/06/2026 → 31/12/2026** |

## 2. TVA — Régime réel normal

- **CA3 mensuelle**, n° FR95105991475.
- ⚠️ **Suppression du régime simplifié (CA12) au 01/01/2027** (art. 38 LF 2025) :
  sans effet ici (déjà en réel normal), mais à garder en tête pour les conseils.
- Déclaration **le 15 du mois suivant** (ou 24 selon régime / télédéclaration).

### 2.1 Deux régimes de TVA possibles ⚠️

L'activité comporte **deux natures de prestations** :

| Nature | Régime | Comptes |
|---|---|---|
| **Conseil / développement / prestation informatique** | TVA **20 %** | `445710` (collectée), `706000`/`706100` (produits) |
| **Formation / enseignement** | **Exonération possible** art. **261-4-4° CGI** | `706700` produit exonéré ; **pas** de `445710` |

> **Contrôle bloquant** : avant chaque CA3, déterminer pour chaque facture client si
> elle relève de la **prestation** (TVA 20 %) ou de la **formation exonérée**.
> L'exonération 261-4-4° est **conditionnée** (établissement d'enseignement,
> caractère de formation professionnelle…) : **statut À CONFIRMER avec l'expert-comptable**.

### 2.2 TVA déductible

| Cas | Compte | Traitement |
|---|---|---|
| Achat France avec facture conforme | `445660` | TVA récupérable |
| Achat UE — autoliquidation | `445200` (ded) + `445200` (coll) | Mention « autoliquidation » obligatoire |
| Achat hors UE (SaaS US…) | — | TVA non facturée, **non déductible** ; TVA dans le coût |
| Sans justificatif attaché | — | **Non déductible par défaut** (alerte A2) |
| Dépense étrangère à l'exploitation | — | **Non déductible** (alerte A3) |

### 2.3 Autoliquidation UE — écriture type

```
Journal : AC   Date : JJ/MM/AAAA   Libellé : Facture {fournisseur} {n°} — autoliquidation
  Débit  611000 — Services extérieurs               {HT}
  Débit  445200 — TVA déductible intracommunautaire {TVA}
  Crédit 401000 — Fournisseurs                      {HT + TVA}
  Crédit 445200 — TVA collectée intracommunautaire  {TVA}
```

## 3. Impôt sur les sociétés (IS)

- Taux normal : **25 %**.
- Taux réduit **15 %** sur les **premiers 42 500 €** de bénéfice : conditions
  (CA < 10 M€, capital **entièrement libéré**, détenu à ≥ 75 % par des personnes
  physiques). ⚠️ **Le statut de libération du capital est À CONFIRMER** (alerte A7).
- **Exercice long (19 mois)** : le seuil de 42 500 € est **proratisé** en fonction de
  la durée de l'exercice. À traiter correctement en clôture.
- Acomptes trimestriels (4 × 25 %) à partir de l'exercice suivant si IS ≥ 3 000 € ;
  **exonération du 1er acompte** pour le 1er exercice.
- Rémunération du Président : **0 €** → aucun produit déductible, aucun `421000`.
- Dividendes : **0 €** → aucun compte `457000`.

## 4. CFE — Cotisation foncière des entreprises

- **CFE due** (confirmé).
- Provision : `444000` (État, impôts sur les bénéfices) ou, plus précis,
  `448600` / `635110` (CFE) selon l'organisation retenue — **discipline à confirmer**.
- Suivi : avis dans l'**espace professionnel impots.gouv.fr**, paiement par
  prélèvement ou à l'échéance.
- Minimum de perception la 1re année, exonération possible (délibération locale).

## 5. Amortissements et immobilisations

**Règle retenue (option « PCG stricte »)** :

- Tout bien **> 500 € HT unitaire** procurant un avantage > 1 an ⇒ **immobilisation**.
- Tout bien **≤ 500 € HT** ⇒ **charge** (compte `606xxx`).

### 5.1 Traitement du matériel déjà passé en charge ⚠️

Le matériel acquis a été **initialement imputé en charge** (ex. `606300`). En clôture :

1. **Recenser** les achats > 500 € HT (alerte A8).
2. **Valider avec l'utilisateur** le reclassement (obligatoire avant écriture).
3. Écritures de régularisation :

```
a) Reclassement de la charge en immobilisation
   Journal : OD  Date : 31/12/AAAA   Libellé : Reclassement {libellé}, facture {n°}
     Débit  218300 — Matériel de bureau et informatique   {HT}
     Crédit 606300 — Fournitures informatiques            {HT}

b) Amortissement linéaire, prorata temporis (matériel info : 3 ans)
   Journal : OD  Date : 31/12/AAAA   Libellé : Dotation {libellé}
     Débit  681100 — Dotations aux amortissements           {annuité}
     Crédit 281830 — Amort. matériel de bureau/informatique {annuité}
```

> ℹ️ Le reclassement modifie le **résultat** (charge → dotation moindre la 1re année)
> et le **bilan** (immobilisation brute + amortissement cumulé). C'est un **écart
> probable avec l'EC** → à documenter dans `cabinet-doublon.md`.

## 6. Clôture annuelle et affectation du résultat

1. **Écritures d'inventaire** : amortissements, dépréciations, charges à payer,
   produits à recevoir, provisions (dont CFE), régularisations de TVA.
2. **Réserve légale** : dotation de **10 % du capital** ⇒ **100 €** (capital 1 000 €),
   prélevée sur le bénéfice jusqu'à atteindre le seuil légal.
3. **AG d'approbation des comptes** dans les **6 mois** de la clôture.
4. **Résultat** : report à nouveau (`110000` / `119000`) ou distribution
   (`457000` → pour 2026, **aucune distribution**).
5. **Liasse fiscale** : 2065 + **2033-A/B** (régime simplifié *des personnes morales*,
   distinct de la TVA), télétransmise via l'**espace professionnel impots.gouv.fr**.
   ⚠️ **L'EFI ne s'applique pas** aux SASU (réservé aux particuliers).
6. **FEC** obligatoire en cas de contrôle (art. A.47 A-1 LPF) — cf. `generer_fec.py`.

## 7. Échéancier type (exercice en cours)

| Échéance | Obligation |
|---|---|
| Mensuel, le 15/24 | **CA3** TVA |
| 15/03, 15/06, 15/09, 15/12 | Acomptes IS (à partir de N+1) |
| 31/12 | CFE (paiement selon avis) |
| ≤ 6 mois après clôture | AG d'approbation |
| Après AG | Liasse 2065 + 2033-A/B |

## 8. Réforme e-invoicing

- 🇫🇷 **01/09/2026** : obligation de **recevoir** les factures électroniques via
  **Plateforme Agréée** pour **toutes** les entreprises ; émission progressive
  (grandes entreprises / ETI depuis 09/2026, puis PME/TPE au **01/09/2027**).
- **Qonto est Plateforme Agréée certifiée** → canal naturel pour LR Data.
- Format : **Factur-X** (PDF/A-3 + XML CII, EN 16931) ; annuaire national.
- Cf. `docs/procedures/06-e-invoicing.md` et `memory-bank/e-invoicing.md`.

## 9. Réserve — non-juriste

Ces règles sont **documentées et à valider**. Elles ne se substituent ni à l'EC en
poste, ni à un conseil fiscal personnalisé.
