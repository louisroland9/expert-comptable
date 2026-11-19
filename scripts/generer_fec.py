#!/usr/bin/env python3
"""Génération d'un FEC conforme à l'article A.47 A-1 du LPF — LR Data (SASU).

Produit un « fichier des écritures comptables » au format normalisé :
18 colonnes obligatoires, séparateur configurable (pipe `|` par défaut,
ou tabulation), décimales à la **virgule**, encodage UTF-8, extension `.txt`.

Colonnes et ordre imposés par l'article A.47 A-1 du LPF
-------------------------------------------------------
 1  JournalCode
 2  JournalLib
 3  EcritureNum
 4  EcritureDate        (AAAAMMJJ)
 5  CompteNum
 6  CompteLib
 7  CompAuxNum
 8  CompAuxLib
 9  PieceRef
10  PieceDate           (AAAAMMJJ)
11  EcritureLib
12  Debit               (décimal, virgule)
13  Credit              (décimal, virgule)
14  EcritureLet
15  DateLet             (AAAAMMJJ)
16  ValidDate           (AAAAMMJJ)
17  Montantdevise
18  Idevise

Entrées
-------
Les journaux sont lus depuis les fichiers JSON/CSV de ``exports-fiscaux/``
(même format que ``verifier_equilibre.py``).

Sécurité
--------
  * Le FEC n'est écrit que si le contrôle d'équilibre global est satisfaisant ;
  * un fichier compagnon ``.meta.json`` documente les entrées, leurs empreintes
    SHA-256 et les totaux générés.

Usage
-----
    python3 scripts/generer_fec.py --siren 105991475 --exercice 2026
    python3 scripts/generer_fec.py --dir exports-fiscaux --sep "|" --sortie exports-fiscaux/fec

Codes de sortie
---------------
    0  FEC généré, équilibre vérifié
    2  déséquilibre : aucun FEC écrit
    3  erreur d'entrée
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

# Réutilisation du lecteur et du contrôleur du script d'équilibre
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_equilibre import (  # noqa: E402
    LecteurErreur,
    charger_journaux,
    controler_ensemble,
    fmt,
    lister_fichiers,
    parse_montant,
)

__version__ = "1.0.0"

ZERO = Decimal("0.00")
CENT = Decimal("0.01")

# Libellés usuel des codes de journal (surchargeables par la table de correspondance)
LIBELLES_JOURNAUX = {
    "AC": "Journal des achats",
    "VE": "Journal des ventes",
    "BQ": "Journal de banque",
    "OD": "Journal des operations diverses",
    "AN": "A-nouveaux",
    "EX": "Journal extra-comptable",
    "CA": "Journal de caisse",
}

COLONNES = [
    "JournalCode", "JournalLib", "EcritureNum", "EcritureDate",
    "CompteNum", "CompteLib", "CompAuxNum", "CompAuxLib",
    "PieceRef", "PieceDate", "EcritureLib", "Debit", "Credit",
    "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise",
]


def vers_aaaammjj(date: str) -> str:
    """Convertit JJ/MM/AAAA ou AAAA-MM-JJ en AAAAMMJJ (format FEC)."""
    texte = (date or "").strip()
    for format_source in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return _dt.datetime.strptime(texte, format_source).strftime("%Y%m%d")
        except ValueError:
            continue
    # Déjà au bon format ?
    if len(texte) == 8 and texte.isdigit():
        return texte
    return ""


def montant_fec(montant: Decimal) -> str:
    """Montant au format FEC : 2 décimales, virgule, sans séparateur de milliers."""
    return f"{montant.quantize(CENT):.2f}".replace(".", ",")


def format_date_lisible(aaaammjj: str) -> str:
    try:
        return _dt.datetime.strptime(aaaammjj, "%Y%m%d").strftime("%d/%m/%Y")
    except ValueError:
        return aaaammjj


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def construire_lignes(journaux, siren: str) -> list[list[str]]:
    """Construit les lignes du FEC (18 colonnes) à partir des journaux.

    Les écritures sont triées par date puis par numéro d'écriture, comme
    l'exige la structuration attendue du FEC.
    """
    lignes: list[list[str]] = []

    for journal in journaux:
        libelle_journal = LIBELLES_JOURNAUX.get(journal.code, journal.code)
        ecritures_triees = sorted(
            journal.ecritures,
            key=lambda e: (vers_aaaammjj(e.date), str(e.numero).zfill(10)),
        )

        for ecriture in ecritures_triees:
            date_fec = vers_aaaammjj(ecriture.date)
            for ligne in ecriture.lignes:
                # CompAuxNum / CompAuxLib : renseignés pour les comptes de tiers
                compte_aux = ligne.compte if ligne.compte[:1] == "4" else ""
                libelle_aux = ligne.libelle if compte_aux else ""
                lignes.append([
                    journal.code,                      # JournalCode
                    libelle_journal,                   # JournalLib
                    str(ecriture.numero).zfill(10),    # EcritureNum
                    date_fec,                          # EcritureDate
                    ligne.compte,                      # CompteNum
                    ligne.libelle,                     # CompteLib
                    compte_aux,                        # CompAuxNum
                    libelle_aux,                       # CompAuxLib
                    ecriture.piece,                    # PieceRef
                    date_fec,                          # PieceDate
                    ecriture.libelle or ligne.libelle, # EcritureLib
                    montant_fec(ligne.debit),          # Debit
                    montant_fec(ligne.credit),         # Credit
                    "",                                # EcritureLet (lettrage)
                    "",                                # DateLet
                    date_fec,                          # ValidDate
                    "",                                # Montantdevise
                    "",                                # Idevise
                ])

    return lignes


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Genere un FEC conforme a l'article A.47 A-1 du LPF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    analyseur.add_argument("--dir", dest="racine", default=None,
                           help="repertoire des journaux (defaut : exports-fiscaux/)")
    analyseur.add_argument("--sortie", dest="sortie", default=None,
                           help="repertoire de sortie du FEC (defaut : exports-fiscaux/fec/)")
    analyseur.add_argument("--siren", dest="siren", default="105991475",
                           help="SIREN de l'entite (defaut : 105991475)")
    analyseur.add_argument("--exercice", dest="exercice", default="2026",
                           help="exercice (defaut : 2026)")
    analyseur.add_argument("--cloture", dest="cloture", default="20271231",
                           help="date de cloture AAAAMMJJ (defaut : 20271231)")
    analyseur.add_argument("--sep", dest="separateur", default="|",
                           help="separateur de colonnes (defaut : '|')")
    analyseur.add_argument("--dry-run", action="store_true",
                           help="controle et affiche sans ecrire le FEC")
    analyseur.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    options = analyseur.parse_args(argv)

    projet = Path(__file__).resolve().parent.parent
    racine = Path(options.racine).expanduser().resolve() if options.racine \
        else (projet / "exports-fiscaux")
    dossier_sortie = Path(options.sortie).expanduser().resolve() if options.sortie \
        else (racine / "fec")

    if not racine.exists():
        print(f"ERREUR : repertoire introuvable : {racine}", file=sys.stderr)
        return 3

    journaux = []
    for fichier in lister_fichiers(racine):
        try:
            journaux.extend(charger_journaux(fichier))
        except LecteurErreur as exc:
            print(f"ERREUR : {fichier} : {exc}", file=sys.stderr)
            return 3

    if not journaux:
        print(f"ERREUR : aucun journal trouve dans {racine}", file=sys.stderr)
        return 3

    anomalies_equilibre = [a for a in controler_ensemble(journaux) if a.niveau == 2]
    total_debit = sum((j.total_debit for j in journaux), ZERO)
    total_credit = sum((j.total_credit for j in journaux), ZERO)
    ecart = (total_debit - total_credit).quantize(CENT)

    print("=" * 78)
    print(" GENERATION DU FEC - LR Data (SASU)")
    print("=" * 78)
    print(f" SIREN            : {options.siren}")
    print(f" Exercice         : {options.exercice}")
    print(f" Date de cloture  : {format_date_lisible(options.cloture)}")
    print(f" Journaux lus     : {len(journaux)}")
    print(f" Total debit      : {fmt(total_debit)}")
    print(f" Total credit     : {fmt(total_credit)}")
    print(f" Ecart            : {fmt(ecart)}")
    print("-" * 78)

    if ecart != ZERO or anomalies_equilibre:
        print(" REFUS DE GENERATION : le jeu d'ecritures n'est pas equilibre.")
        for anomalie in anomalies_equilibre:
            print(f"   - {anomalie.source} : {anomalie.message}")
        print("=" * 78)
        return 2

    lignes = construire_lignes(journaux, options.siren)
    print(f" Lignes FEC       : {len(lignes)}")

    if options.dry_run:
        print(" Mode --dry-run : aucun fichier ecrit.")
        print("=" * 78)
        return 0

    dossier_sortie.mkdir(parents=True, exist_ok=True)
    chemin_fec = dossier_sortie / f"{options.siren}FEC{options.cloture}.txt"

    contenu = options.separateur.join(COLONNES) + "\n"
    contenu += "".join(options.separateur.join(l) + "\n" for l in lignes)
    chemin_fec.write_text(contenu, encoding="utf-8")

    empreintes = {}
    for fichier in lister_fichiers(racine):
        try:
            cle = str(fichier.relative_to(projet))
        except ValueError:
            # Le fichier est hors de l'arborescence du projet (ex. test dans /tmp).
            cle = str(fichier)
        empreintes[cle] = sha256_fichier(fichier)

    meta = {
        "script": "generer_fec.py",
        "version": __version__,
        "execution": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "fec": str(chemin_fec),
        "siren": options.siren,
        "exercice": options.exercice,
        "date_cloture": options.cloture,
        "separateur": options.separateur,
        "nb_colonnes": len(COLONNES),
        "nb_journaux": len(journaux),
        "nb_lignes": len(lignes),
        "total_debit": str(total_debit),
        "total_credit": str(total_credit),
        "ecart": str(ecart),
        "equilibre": ecart == ZERO,
        "sha256_entrees": empreintes,
    }
    chemin_meta = chemin_fec.with_suffix(chemin_fec.suffix + ".meta.json")
    chemin_meta.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f" FEC ecrit        : {chemin_fec}")
    print(f" Tracabilite      : {chemin_meta}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
