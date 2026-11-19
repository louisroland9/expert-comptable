# exports-fiscaux

Livrables comptables et fiscaux **générés** par les scripts Python.

## Arborescence

```
exports-fiscaux/
├── journaux/   # Journaux comptables (AC, VE, BQ, OD, AN)
├── tva/        # Calculs de TVA et pré-maquettes de CA3
└── fec/        # Fichier des Écritures Comptables (art. A.47 A-1 LPF)
```

## Règle de production

> Un livrable n'est écrit **que si le contrôle d'équilibre est satisfaisant**
> (Σ Débit == Σ Crédit). Sinon, le script **refuse** d'écrire et retourne un code
> de sortie non nul.

## Formats

### Journaux (`journaux/`)

**JSON** (format de travail du harnais) :

```json
{
  "journal": "AC",
  "periode": "2026-11",
  "ecritures": [
    {
      "date": "05/11/2026",
      "numero": "1",
      "libelle": "Facture Qonto abonnement",
      "piece": "FAC-QONTO-2026-10",
      "lignes": [
        {"compte": "627800", "libelle": "Services bancaires", "debit": "12,90", "credit": "0,00"},
        {"compte": "445660", "libelle": "TVA deductible",     "debit": "2,58",  "credit": "0,00"},
        {"compte": "401000", "libelle": "Fournisseurs",       "debit": "0,00",  "credit": "15,48"}
      ]
    }
  ]
}
```

**CSV** (une ligne par ligne d'écriture) :

```csv
journal,date,ecriture_num,compte,libelle,debit,credit,piece
AC,05/11/2026,1,627800,Services bancaires,12.90,0.00,FAC-QONTO-2026-10
AC,05/11/2026,1,445660,TVA deductible,2.58,0.00,FAC-QONTO-2026-10
AC,05/11/2026,1,401000,Fournisseurs,0.00,15.48,FAC-QONTO-2026-10
```

Montants acceptés avec **point ou virgule** décimale.

### FEC (`fec/`)

- Nom : `{SIREN}FEC{AAAAMMJJ}.txt` (ex. `105991475FEC20271231.txt`)
- 18 colonnes séparées par `|`, encodage UTF-8, décimales à la **virgule**
- Tri par `EcritureDate` puis `EcritureNum`

### Traçabilité

Chaque livrable est accompagné d'un fichier `.meta.json` (SHA-256 des entrées,
totaux, paramètres, horodatage). Ces fichiers sont exclus du versionnement.

## Fichiers attendus (état actuel)

| Fichier | Statut |
|---|---|
| — | ⏳ Aucun journal généré (aucun snapshot Qonto encore extrait) |
