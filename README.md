# expert-comptable — harnais comptable et fiscal SASU

Tenue comptable et fiscale **en parallèle** de l'expert-comptable (mode doublon) pour
la **SASU LR Data** — PCG 2025/2026, TVA (CA3), IS, FEC, MCP Qonto.

> ⚠️ **Avertissement permanent** — Ce dépôt est un **outil d'assistance**. Un
> **expert-comptable est toujours en poste** et reste la **référence légale**.
> Aucun livrable produit ici n'est **opposable** en l'état : tout journal, FEC ou CA3
> est un **projet de travail**. Le harnais ne remplace pas la responsabilité d'un
> expert-comptable inscrit à l'Ordre.

## 1. Périmètre

| Élément | Valeur |
|---|---|
| Entité | **LR Data** — SASU, associé unique |
| SIREN / RCS | **105 991 475** R.C.S. Paris |
| N° TVA intracommunautaire | **FR95105991475** |
| Siège | 47 rue Vivienne, 75002 Paris |
| Exercice social (statuts) | **09/06/2026 → 31/12/2027** (exercice long, ~19 mois) |
| **Périmètre doublon (traité ici)** | **09/06/2026 → 31/12/2026** |
| Régime TVA | Réel normal — **CA3 mensuelle** |
| Banque | **Qonto** (1re transaction : 09/06/2026) |

> 🔴 **Règle temporelle stricte** : toute écriture **antérieure au 09/06/2026** est
> **hors périmètre** (alerte bloquante). La période 05→08/06/2026 relève de l'EC.
> Cf. `.clinerules/01-persona-sasu.md` (R4).

## 2. Arborescence

```
expert-comptable/
├── .clinerules/                  # Règles de l'agent (source de vérité des consignes)
│   ├── 01-persona-sasu.md            # Rôle, alertes A1→A10, format des écritures
│   ├── 02-workflow-mcp-qonto.md      # Serveur MCP Qonto, snapshots, outils autorisés
│   ├── 03-regles-calculs-python.md   # Decimal, équilibre, codes de sortie, traçabilité
│   ├── 04-cycle-fiscal-sasu.md       # TVA, IS, CFE, amortissements, clôture, e-invoicing
│   ├── 05-protocole-memoire.md       # Lecture/écriture de memory-bank/
│   ├── 06-e-invoicing.md             # Réforme facturation électronique, Factur-X
│   ├── 07-workflow-git.md            # Branches, Conventional Commits, interdictions
│   └── 08-documentation.md           # Mise à jour obligatoire de ce README
├── memory-bank/                  # Mémoire persistante du dossier (versionnée)
│   ├── identite-sasu.md              # Fiche juridique et fiscale (Kbis)
│   ├── suivi-exercice.md             # Tableau de bord + dernier ID Qonto traité
│   ├── mapping-qonto-pcg.md          # Contrepartie Qonto → compte PCG
│   ├── plan-comptable-sasu.md        # Plan de comptes réellement retenu
│   ├── cabinet-doublon.md            # Questions, décisions (D-{NN}), écarts avec l'EC
│   ├── e-invoicing.md                # État de conformité e-invoicing
│   └── immobilisations-et-charges.md # Registre du matériel (> 500 € HT)
├── scripts/                      # Outils Python (stdlib pure — cf. règle R3/03)
│   ├── verifier_equilibre.py         # Contrôle d'équilibre des journaux
│   ├── generer_fec.py                # FEC (art. A.47 A-1 LPF)
│   ├── calculer_tva.py               # TVA + pré-maquette CA3 (lecture seule)
│   ├── amortissements.py             # Module : dotations et reclassements (API, sans CLI)
│   ├── comparer_avec_ec.py           # Comparaison avec la balance de l'EC
│   ├── verifier_conflits.py          # Hook : marqueurs de conflit git
│   └── creer_branche.sh              # Création de branche (feat|fix|chore|docs)
├── qonto-exports/                # 🔒 Snapshots bruts Qonto (NON VERSIONNÉ)
├── reference-expert-comptable/   # 🔒 Livrables EC (NON VERSIONNÉ, lecture seule)
├── exports-fiscaux/              # 📤 Livrables générés (NON VERSIONNÉ)
│   ├── journaux/                     # Journaux AC, VE, BQ, OD, AN
│   ├── tva/                          # Calculs TVA et pré-CA3
│   └── fec/                          # FEC conforme
├── pyproject.toml                # Projet uv, dépendances, entry points
├── .pre-commit-config.yaml       # Garde-fous (données financières, commits, README)
└── README.md                     # Ce fichier
```

## 3. Installation

Projet géré avec **`uv`** (Python ≥ 3.12 requis ; 3.12.3 en place).

```bash
uv sync                                        # crée .venv/ et installe l'outillage
uv run pre-commit install --install-hooks      # active les hooks (pre-commit + commit-msg)
git config commit.template .gitmessage          # modèle de message de commit
```

> Le `core.hooksPath` posé par pre-commit est **local et non versionné** : un clone
> neuf doit relancer ces commandes (cf. `.clinerules/07-workflow-git.md`, R1).

Vérifier l'ensemble du dépôt sans committer :

```bash
uv run pre-commit run --all-files
```

## 4. Scripts

Tous les scripts sont **stdlib pure** (aucune dépendance externe requise) et
respectent la règle R3/03. Ils lisent leurs entrées en **lecture seule** et écrivent
exclusivement dans `exports-fiscaux/`.

Deux invocations sont possibles : l'appel direct, ou l'**entry point** déclaré dans
`pyproject.toml` (via `uv run`).

| Script | Entry point | But | Entrée | Sortie |
|---|---|---|---|---|
| `verifier_equilibre.py` | `equilibre` | Contrôle d'équilibre (écriture / journal / global) | journaux `exports-fiscaux/` | rapport (+ `.meta.json` si `--meta`) |
| `generer_fec.py` | `fec` | FEC conforme art. A.47 A-1 | journaux `exports-fiscaux/` | `exports-fiscaux/fec/{SIREN}FEC{AAAAMMJJ}.txt` |
| `calculer_tva.py` | `tva` | TVA collectée/déductible + pré-CA3 | journaux `exports-fiscaux/` | rapport console (lecture seule) |
| `comparer_avec_ec.py` | `comparer` | Écarts avec la balance de l'EC | nos journaux + `reference-expert-comptable/` | rapport d'écarts |
| `amortissements.py` | — (module) | Lecture du registre + calcul des dotations/reclassements | `memory-bank/immobilisations-et-charges.md` | objets `Ecriture` (API, pas de CLI) |
| `verifier_conflits.py` | — | Marqueurs de conflit git (hook) | fichiers passés en argument | code de sortie |
| `creer_branche.sh` | — | Création d'une branche de travail | `<feat\|fix\|chore\|docs> <slug>` | branche locale |

> ℹ️ Les **entry points** sont exposés par `[project.scripts]` (le projet est packagé
> pour cela, sans dépendance runtime ajoutée). Les scripts restent exécutables en
> **stdlib pure** par appel direct.

### 4.1 Contrôle d'équilibre

```bash
uv run equilibre                    # ou : python3 scripts/verifier_equilibre.py
uv run equilibre --json             # sortie machine
uv run equilibre --dir <chemin>     # autre répertoire
uv run equilibre --meta             # écrit un .meta.json de traçabilité
```

Par écriture, par journal et globalement : **Σ Débit == Σ Crédit**. Un déséquilibre
**bloque** la production des livrables.

### 4.2 FEC

```bash
uv run fec --siren 105991475 --exercice 2026      # défauts : SIREN/TVA LR Data
uv run fec --cloture 20271231 --sep "|" --dry-run # contrôle sans écrire
```

- Nom du fichier : `{SIREN}FEC{AAAAMMJJ}.txt` (défaut `105991475FEC20271231.txt`)
- 18 colonnes (art. A.47 A-1), séparateur `|` (ou tabulation), **virgule** décimale,
  UTF-8, tri par `EcritureDate` puis `EcritureNum`.

### 4.3 TVA / CA3

```bash
uv run tva --mois 2026-11
uv run tva --debut 2026-06-09 --fin 2026-12-31
uv run tva --comptes-exoneres 70670 --json     # comptes traités comme exonérés
```

> ⚠️ **Double régime TVA** — les prestations informatiques relèvent de la TVA **20 %**
> (`706000`), la **formation / enseignement** pourrait relever de l'**exonération
> art. 261-4-4° CGI** (`706700`). L'exonération n'est **jamais présumée** : le script
> **alerte** sur les comptes exonérés (défaut `70670`). Question ouverte E4.

### 4.4 Amortissements

`scripts/amortissements.py` est un **module bibliothèque** : il expose
`lire_registre()` et `construire_ecritures()` (aucune fonction `main`, aucune CLI à ce
jour). Il lit le **registre des immobilisations**, calcule les dotations (**linéaire
3 ans, 33,33 %**, prorata en jours — décision D-07) et les écritures de reclassement
(PCG stricte, D-09), puis **retourne des objets `Ecriture`** (format de
`verifier_equilibre.py`).

```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); \
import amortissements as a; \
biens, anomalies = a.lire_registre(__import__('pathlib').Path('memory-bank/immobilisations-et-charges.md')); \
print(len(biens), 'bien(s)', len(anomalies), 'anomalie(s)')"
```

> ⚠️ **Registre vide** → aucun bien, aucune écriture. Le registre est lu en **lecture
> seule**. La docstring du module décrit une CLI (`--registre`, `--sortie`, codes de
> sortie `0/1/2/3`) qui **n'existe pas encore** : écart signalé, cf.
> `memory-bank/cabinet-doublon.md` (D-10).

### 4.5 Comparaison avec l'expert-comptable

```bash
uv run comparer                       # mode veille (code 4) si aucune balance EC
uv run comparer --tolerance 1.00      # tolérance d'écart en euros
```

### 4.6 Codes de sortie

| Code | Signification |
|---|---|
| `0` | Succès, équilibre vérifié |
| `1` | Succès technique, **anomalies détectées** (avertissements) |
| `2` | **Déséquilibre** ou erreur de structure → livrable non validé |
| `3` | Erreur d'entrée (fichier manquant, JSON/CSV invalide) |
| `4` | Aucune balance EC disponible (mode veille de `comparer`) |

Chaque livrable est accompagné d'un **`.meta.json`** (SHA-256 des entrées, totaux,
paramètres, horodatage). Ces fichiers compagnons sont **exclus du versionnement**.

## 5. Workflow git

- **Une tâche = une branche** (`feat/…`, `fix/…`, `chore/…`, `docs/…`), créée depuis
  `main`. **Jamais de commit direct sur `main`** — cf. `.clinerules/07`, R2.1.
  ```bash
  bash scripts/creer_branche.sh docs readme-racine
  ```
- **Conventional Commits**, validés par `cz check` (hook `commit-msg`) :
  ```
  <type>(<scope>): <description à l'infinitif, ≤ 72 caractères>
  ```
- **`git push` est fait par l'utilisateur.** L'agent ne pousse ni ne merge jamais.
- Un **écart avec l'EC** se documente dans `memory-bank/cabinet-doublon.md`, **dans le
  même commit** que le changement.

## 6. Règles d'or

| # | Règle |
|---|---|
| 1 | **Sources immuables** — `qonto-exports/` et `reference-expert-comptable/` ne sont **jamais** modifiés, renommés ni supprimés. |
| 2 | **Aucun calcul de tête** — tout montant passe par un script Python (`Decimal`, jamais de `float`) ; la sortie console est citée comme source. |
| 3 | **Équilibre bloquant** — Σ Débit == Σ Crédit, sinon aucun livrable n'est écrit. |
| 4 | **Aucune donnée financière versionnée** — snapshots, livrables, justificatifs et `.meta.json` sont exclus (`.gitignore` + hooks). |
| 5 | **Comptes PCG cités** — numéro **et** intitulé exacts (ex. `606300 — Fournitures informatiques`). |
| 6 | **Aucun montant inventé** — un montant estimé porte la mention `⚠️ ESTIMÉ — À CONFIRMER`. |
| 7 | **Aucune donnée Qonto hors du workspace** — le MCP alimente, Python calcule. |

## 7. Alertes systématiques

Ces points déclenchent une alerte explicite (détail et traitement dans
`.clinerules/01-persona-sasu.md`) :

| # | Situation | Gravité |
|---|---|---|
| A1 | Compte courant d'associé `455100` **débiteur** en SASU (abus de bien social) | 🔴 **BLOQUANT** |
| A2 | Transaction Qonto **sans justificatif** (TVA non déductible par défaut) | 🟠 Élevée |
| A3 | **TVA non récupérable** | 🟠 Élevée |
| A4 | **Autoliquidation UE** (`445200`, mention obligatoire) | 🟠 Élevée |
| A5 | **Achat hors UE** (SaaS US…) — TVA non déductible | 🟠 Élevée |
| A6 | **Formation / enseignement** — exonération art. 261-4-4° CGI | 🟠 Élevée |
| A7 | **Capital social non libéré** (`109000` > 0) | 🟡 Moyenne |
| A8 | Dépense **> 500 € HT** unitaire passée en charge | 🟡 Moyenne |
| A9 | **CFE** non provisionnée | 🟡 Moyenne |
| A10 | Justificatif **hors e-invoicing** (non Factur-X) | 🟡 Moyenne |

## 8. Maintenance de ce README

> 📌 **Toute tâche qui modifie l'arborescence, les scripts ou les entry points met à
> jour ce README *dans le même commit*.** Règle complète :
> `.clinerules/08-documentation.md`.
>
> Un hook pre-commit **avertisseur** (`readme-a-jour`) rappelle cette obligation si un
> commit touche `scripts/`, `.clinerules/`, `memory-bank/` ou `pyproject.toml` sans
> toucher `README.md`. Contournement volontaire :
> `SKIP=readme-a-jour git commit …`.

## 9. Références

- Règles de l'agent : `.clinerules/01` → `.clinerules/08`
- Mémoire du dossier : `memory-bank/`
- Convention de commit : `.gitmessage`
- Modèle de pull request : `.github/PULL_REQUEST_TEMPLATE.md`
- Protocole mémoire (lecture obligatoire en début de session) :
  `.clinerules/05-protocole-memoire.md`
