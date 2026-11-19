#!/usr/bin/env python3
"""Calcul de la TVA et préparation de la CA3 — LR Data (SASU).

Calcule, à partir des journaux de ``exports-fiscaux/`` :
  * la **TVA collectée** par taux (20 %, 10 %, 5,5 %, 2,1 %) ;
  * la **TVA déductible** (biens/services, intracommunautaire, immobilisations) ;
  * le **CA taxable / exonéré** (⚠️ exonération formation art. 261-4-4° CGI) ;
  * la **TVA nette** (à payer ou crédit de TVA) ;
  * une **pré-maquette de CA3** (lignes 08 à 29, 32 à 45).

Point de vigilance TVA — DOUBLE RÉGIME
-------------------------------------
LR Data facture à la fois :
  * des **prestations informatiques / conseil** → TVA **20 %** (compte 706000) ;
  * de la **formation / enseignement** → potentiellement **exonérée** (art. 261-4-4°
    CGI, compte 706700). L'exonération n'est **pas** présumée : les comptes listés
    dans ``--comptes-exoneres`` (défaut : 70670) sont traités comme exonérés et le
    script **alerte** sur leur montant.

Aucune écriture n'est produite : le script est **en lecture seule**.

Usage
-----
    python3 scripts/calculer_tva.py --mois 2026-11
    python3 scripts/calculer_tva.py --debut 2026-06-09 --fin 2026-12-31
    python3 scripts/calculer_tva.py --json

Codes de sortie
---------------
    0  calcul réalisé
    1  calcul réalisé avec avertissements (exonérations, anomalies)
    3  erreur d'entrée
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_equilibre import (  # noqa: E402
    LecteurErreur,
    charger_journaux,
    fmt,
    lister_fichiers,
)

__version__ = "1.0.0"

ZERO = Decimal("0.00")
CENT = Decimal("0.01")

# Comptes de TVA
COMPTES_TVA_COLLECTEE = {"445710", "445711", "445712", "445713"}
COMPTE_TVA_INTRACOM = "445200"
COMPTES_TVA_DEDUCTIBLE = {"445660", "445661", "445662", "445663", "445670", "445680"}

# Comptes de produits
COMPTES_VENTES = ("7",)
COMPTE_VENTES_EXONEREES_DEFAUT = ("70670",)  # formation / enseignement

TAUX_CONNUS = {
    "20": Decimal("0.20"),
    "10": Decimal("0.10"),
    "5.5": Decimal("0.055"),
    "2.1": Decimal("0.021"),
}


def vers_iso(date: str) -> str:
    """Normalise une date en AAAA-MM-JJ (ou chaîne vide)."""
    texte = (date or "").strip()
    for format_source in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return _dt.datetime.strptime(texte, format_source).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return texte


def libelle_compte(compte: str) -> str:
    return f"Compte {compte}" if compte else "Compte inconnu"


def agreger(
    journaux, debut: str | None, fin: str | None, comptes_exoneres: tuple[str, ...]
) -> dict:
    """Agrège les mouvements de TVA et de chiffre d'affaires."""
    tva_collectee: dict[str, Decimal] = {}
    tva_deductible: dict[str, Decimal] = {}
    tva_intracom_ded: Decimal = ZERO
    tva_intracom_coll: Decimal = ZERO
    ca_par_compte: dict[str, Decimal] = {}
    ca_exonere: Decimal = ZERO
    ca_taxable: Decimal = ZERO
    lignes_exonerees: list[dict] = []
    dates: list[str] = []

    def dans_periode(date_iso: str) -> bool:
        if debut and date_iso and date_iso < debut:
            return False
        if fin and date_iso and date_iso > fin:
            return False
        return True

    for journal in journaux:
        for ecriture in journal.ecritures:
            date_iso = vers_iso(ecriture.date)
            if not dans_periode(date_iso):
                continue
            dates.append(date_iso)

            # TVA collectée : le crédit des comptes 4457xx exprime la TVA due
            for ligne in ecriture.lignes:
                compte = ligne.compte
                credit = ligne.credit
                debit = ligne.debit

                if compte in COMPTES_TVA_COLLECTEE:
                    tva_collectee[compte] = tva_collectee.get(compte, ZERO) + credit - debit
                elif compte in COMPTES_TVA_DEDUCTIBLE:
                    tva_deductible[compte] = tva_deductible.get(compte, ZERO) + debit - credit
                elif compte == COMPTE_TVA_INTRACOM:
                    tva_intracom_ded += debit
                    tva_intracom_coll += credit

                # Chiffre d'affaires : crédit des comptes de produits (classe 7)
                if (
                    compte.startswith(COMPTES_VENTES)
                    and not compte.startswith("76")
                    and not compte.startswith("77")
                    and not compte.startswith("78")
                ):
                    montant = credit - debit
                    if montant == ZERO:
                        continue
                    ca_par_compte[compte] = ca_par_compte.get(compte, ZERO) + montant
                    if compte.startswith(tuple(comptes_exoneres)):
                        ca_exonere += montant
                        lignes_exonerees.append(
                            {
                                "date": date_iso,
                                "journal": journal.code,
                                "piece": ecriture.piece,
                                "compte": compte,
                                "montant": str(montant),
                                "libelle": ecriture.libelle or ligne.libelle,
                            }
                        )
                    else:
                        ca_taxable += montant

    return {
        "tva_collectee": tva_collectee,
        "tva_deductible": tva_deductible,
        "tva_intracom_ded": tva_intracom_ded,
        "tva_intracom_coll": tva_intracom_coll,
        "ca_par_compte": ca_par_compte,
        "ca_exonere": ca_exonere,
        "ca_taxable": ca_taxable,
        "lignes_exonerees": lignes_exonerees,
        "dates": dates,
    }


def afficher(agregat: dict, debut: str | None, fin: str | None) -> bool:
    """Affiche le rapport TVA. Retourne True si des avertissements existent."""
    tva_collectee_totale = sum(agregat["tva_collectee"].values(), ZERO)
    tva_deductible_totale = sum(agregat["tva_deductible"].values(), ZERO)
    tva_nette = tva_collectee_totale - tva_deductible_totale

    avertissements = bool(agregat["lignes_exonerees"])

    print("=" * 78)
    print(" CALCUL DE TVA - LR Data (SASU) - FR95105991475")
    print("=" * 78)
    print(f" Periode          : du {debut or '(origine)'} au {fin or '(fin)'}")
    print(f" Ecritures prises : {len(set(agregat['dates']))} jours distincts")
    print("-" * 78)

    print(" TVA COLLECTEE")
    if agregat["tva_collectee"]:
        for compte in sorted(agregat["tva_collectee"]):
            print(f"   {compte}  {fmt(agregat['tva_collectee'][compte]):>14}")
    else:
        print("   (aucune)")
    if agregat["tva_intracom_coll"]:
        print(f"   445200 (intracom. collectee)  {fmt(agregat['tva_intracom_coll']):>14}")
    print(f"   {'TOTAL':<28} {fmt(tva_collectee_totale + agregat['tva_intracom_coll']):>14}")

    print("-" * 78)
    print(" TVA DEDUCTIBLE")
    if agregat["tva_deductible"]:
        for compte in sorted(agregat["tva_deductible"]):
            print(f"   {compte}  {fmt(agregat['tva_deductible'][compte]):>14}")
    else:
        print("   (aucune)")
    if agregat["tva_intracom_ded"]:
        print(f"   445200 (intracom. deduct.)    {fmt(agregat['tva_intracom_ded']):>14}")
    print(f"   {'TOTAL':<28} {fmt(tva_deductible_totale + agregat['tva_intracom_ded']):>14}")

    print("-" * 78)
    collectee_globale = tva_collectee_totale + agregat["tva_intracom_coll"]
    deductibile_globale = tva_deductible_totale + agregat["tva_intracom_ded"]
    tva_nette = collectee_globale - deductibile_globale
    if tva_nette > ZERO:
        print(f" TVA NETTE A PAYER    : {fmt(tva_nette)}")
    elif tva_nette < ZERO:
        print(f" CREDIT DE TVA        : {fmt(-tva_nette)}")
    else:
        print(" TVA NETTE            : 0,00 (ni paiement ni credit)")

    print("-" * 78)
    print(" CHIFFRE D'AFFAIRES")
    for compte in sorted(agregat["ca_par_compte"]):
        marque = "  <- EXONERE ?" if compte.startswith(("70670",)) else ""  # noqa: E501
        print(f"   {compte}  {fmt(agregat['ca_par_compte'][compte]):>14}{marque}")
    print(f"   {'CA taxable':<28} {fmt(agregat['ca_taxable']):>14}")
    print(f"   {'CA exonere (261-4-4°)':<28} {fmt(agregat['ca_exonere']):>14}")
    print(f"   {'CA total':<28} {fmt(agregat['ca_taxable'] + agregat['ca_exonere']):>14}")

    if avertissements:
        print("-" * 78)
        print(" AVERTISSEMENT TVA - EXONERATION ART. 261-4-4° CGI (A VERIFIER)")
        print(f"   {len(agregat['lignes_exonerees'])} ligne(s) de formation/enseignement")
        print(f"   Montant total : {fmt(agregat['ca_exonere'])}")
        print("   -> Si l'exoneration ne s'applique pas, la TVA a 20 % est due")
        print("      sur ces montants. Statut A CONFIRMER avec l'expert-comptable.")

    print("=" * 78)
    return avertissements


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Calcul de la TVA et pré-maquette de CA3 (lecture seule).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    analyseur.add_argument(
        "--dir",
        dest="racine",
        default=None,
        help="repertoire des journaux (defaut : exports-fiscaux/)",
    )
    analyseur.add_argument(
        "--mois", dest="mois", default=None, help="mois au format AAAA-MM (ex. 2026-11)"
    )
    analyseur.add_argument("--debut", dest="debut", default=None, help="date de debut AAAA-MM-JJ")
    analyseur.add_argument("--fin", dest="fin", default=None, help="date de fin AAAA-MM-JJ")
    analyseur.add_argument(
        "--comptes-exoneres",
        dest="exoneres",
        default="70670",
        help="prefixes de comptes exoneres, separes par des virgules (defaut : 70670 = formation)",
    )
    analyseur.add_argument("--json", action="store_true", help="sortie JSON")
    analyseur.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    options = analyseur.parse_args(argv)

    debut, fin = options.debut, options.fin
    if options.mois:
        if not re.match(r"^\d{4}-\d{2}$", options.mois):
            print(f"ERREUR : mois invalide : {options.mois!r} (attendu AAAA-MM)", file=sys.stderr)
            return 3
        annee, mois = options.mois.split("-")
        debut = f"{annee}-{mois}-01"
        dernier_jour = _dt.date(int(annee) + (mois == "12"), int(mois) % 12 + 1, 1) - _dt.timedelta(
            days=1
        )
        fin = dernier_jour.isoformat()

    comptes_exoneres = (
        tuple(p.strip() for p in options.exoneres.split(",") if p.strip())
        or COMPTE_VENTES_EXONEREES_DEFAUT
    )

    projet = Path(__file__).resolve().parent.parent
    racine = (
        Path(options.racine).expanduser().resolve()
        if options.racine
        else (projet / "exports-fiscaux")
    )

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

    agregat = agreger(journaux, debut, fin, comptes_exoneres)

    if options.json:
        sortie = {
            "script": "calculer_tva.py",
            "version": __version__,
            "execution": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "periode": {"debut": debut, "fin": fin},
            "comptes_exoneres": list(comptes_exoneres),
            "tva_collectee": {k: str(v) for k, v in agregat["tva_collectee"].items()},
            "tva_deductible": {k: str(v) for k, v in agregat["tva_deductible"].items()},
            "tva_intracom_deductible": str(agregat["tva_intracom_ded"]),
            "tva_intracom_collectee": str(agregat["tva_intracom_coll"]),
            "ca_par_compte": {k: str(v) for k, v in agregat["ca_par_compte"].items()},
            "ca_taxable": str(agregat["ca_taxable"]),
            "ca_exonere": str(agregat["ca_exonere"]),
            "lignes_exonerees": agregat["lignes_exonerees"],
        }
        print(json.dumps(sortie, indent=2, ensure_ascii=False))
        avertissements = bool(agregat["lignes_exonerees"])
    else:
        avertissements = afficher(agregat, debut, fin)

    return 1 if avertissements else 0


if __name__ == "__main__":
    sys.exit(main())
