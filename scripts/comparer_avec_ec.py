#!/usr/bin/env python3
"""Comparaison « doublon » avec les livrables de l'expert-comptable — LR Data.

Mode doublon : l'expert-comptable (EC) reste la référence légale. Ce script
confronte **notre** balance (calculée depuis nos journaux) à la **balance de
l'EC** déposée dans ``reference-expert-comptable/``.

⚠️ **Veille** : tant que ``reference-expert-comptable/`` ne contient pas de
balance, le script le signale et retourne le code 4 (pas d'erreur).

Formats de balance acceptés
---------------------------
A) CSV ``compte;libelle;debit;credit`` (séparateur ``;``, ``,``, `\\t`` ou ``|``)
B) JSON ``{"comptes": [{"compte": "...", "debit": "...", "credit": "..."}]}``

Usage
-----
    python3 scripts/comparer_avec_ec.py
    python3 scripts/comparer_avec_ec.py --tolerance 1.00

Codes de sortie
---------------
    0  comparaison réalisée, écarts sous tolérance
    1  comparaison réalisée, écarts significatifs détectés
    3  erreur d'entrée (journaux illisibles)
    4  aucune balance EC disponible (mode veille)
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_equilibre import (  # noqa: E402
    LecteurErreur,
    charger_journaux,
    fmt,
    lister_fichiers,
    parse_montant,
)

__version__ = "1.0.0"

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def balance_depuis_journaux(journaux) -> dict[str, dict[str, Decimal]]:
    """Construit notre balance {compte: {debit, credit, solde}}."""
    balance: dict[str, dict[str, Decimal]] = {}
    for journal in journaux:
        for ecriture in journal.ecritures:
            for ligne in ecriture.lignes:
                entree = balance.setdefault(ligne.compte, {"debit": ZERO, "credit": ZERO})
                entree["debit"] += ligne.debit
                entree["credit"] += ligne.credit
    for entree in balance.values():
        entree["solde"] = entree["debit"] - entree["credit"]
    return balance


def lire_balance_ec(chemin: Path) -> dict[str, dict[str, Decimal]]:
    """Lit une balance EC (CSV ou JSON) et la normalise."""
    texte = chemin.read_text(encoding="utf-8")
    balance: dict[str, dict[str, Decimal]] = {}

    if chemin.suffix.lower() == ".json":
        document = json.loads(texte)
        entrees = document.get("comptes") if isinstance(document, dict) else document
        if not isinstance(entrees, list):
            raise ValueError("JSON de balance sans liste 'comptes'")
        for entree in entrees:
            compte = str(entree.get("compte", "")).strip()
            if not compte:
                continue
            balance[compte] = {
                "debit": parse_montant(entree.get("debit")),
                "credit": parse_montant(entree.get("credit")),
            }
    else:
        echantillon = texte[:2048]
        try:
            dialecte = csv.Sniffer().sniff(echantillon, delimiters=";,\t|")
        except csv.Error:
            dialecte = csv.excel
            dialecte.delimiter = ";"
        lecteur = csv.DictReader(io.StringIO(texte), dialect=dialecte)
        if not lecteur.fieldnames:
            raise ValueError("CSV de balance sans en-tete")
        for ligne in lecteur:
            normalisee = {(k or "").strip().lower(): (v or "") for k, v in ligne.items()}
            compte = normalisee.get("compte", "").strip()
            if not compte:
                continue
            balance[compte] = {
                "debit": parse_montant(normalisee.get("debit")),
                "credit": parse_montant(normalisee.get("credit")),
            }

    for entree in balance.values():
        entree["solde"] = entree["debit"] - entree["credit"]
    return balance


def comparer(notre: dict, ec: dict, tolerance: Decimal) -> list[dict]:
    """Rapproche les deux balances et liste les écarts > tolerance."""
    ecarts: list[dict] = []
    for compte in sorted(set(notre) | set(ec)):
        n = notre.get(compte, {"debit": ZERO, "credit": ZERO, "solde": ZERO})
        e = ec.get(compte, {"debit": ZERO, "credit": ZERO, "solde": ZERO})
        delta = (n["solde"] - e["solde"]).quantize(CENT)
        delta_debit = (n["debit"] - e["debit"]).quantize(CENT)
        delta_credit = (n["credit"] - e["credit"]).quantize(CENT)

        if (
            abs(delta) <= tolerance
            and abs(delta_debit) <= tolerance
            and abs(delta_credit) <= tolerance
        ):
            continue

        if compte not in notre:
            qualification = "ecriture EC absente chez nous"
        elif compte not in ec:
            qualification = "ecriture chez nous absente chez l'EC"
        else:
            qualification = "imputation ou montant different"

        ecarts.append(
            {
                "compte": compte,
                "notre_debit": str(n["debit"]),
                "notre_credit": str(n["credit"]),
                "notre_solde": str(n["solde"]),
                "ec_debit": str(e["debit"]),
                "ec_credit": str(e["credit"]),
                "ec_solde": str(e["solde"]),
                "delta_solde": str(delta),
                "delta_debit": str(delta_debit),
                "delta_credit": str(delta_credit),
                "qualification": qualification,
            }
        )
    return ecarts


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Compare notre balance avec celle de l'expert-comptable (mode doublon).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    analyseur.add_argument(
        "--dir",
        dest="racine",
        default=None,
        help="repertoire de NOS journaux (defaut : exports-fiscaux/)",
    )
    analyseur.add_argument(
        "--ec",
        dest="dossier_ec",
        default=None,
        help="repertoire des livrables EC (defaut : reference-expert-comptable/)",
    )
    analyseur.add_argument(
        "--tolerance",
        dest="tolerance",
        default="0.00",
        help="tolerance en euros sur les ecarts (defaut : 0)",
    )
    analyseur.add_argument("--json", action="store_true", help="sortie JSON")
    analyseur.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    options = analyseur.parse_args(argv)

    tolerance = parse_montant(options.tolerance)

    projet = Path(__file__).resolve().parent.parent
    racine = (
        Path(options.racine).expanduser().resolve()
        if options.racine
        else (projet / "exports-fiscaux")
    )
    dossier_ec = (
        Path(options.dossier_ec).expanduser().resolve()
        if options.dossier_ec
        else (projet / "reference-expert-comptable")
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

    notre_balance = balance_depuis_journaux(journaux)

    print("=" * 78)
    print(" COMPARAISON DOUBLON - LR Data (SASU)")
    print("=" * 78)
    print(f" Nos journaux     : {racine}  ({len(journaux)} journal(aux))")
    print(f" Comptes pointes  : {len(notre_balance)}")
    print(f" Livrables EC     : {dossier_ec}")

    fichiers_ec = []
    if dossier_ec.exists():
        fichiers_ec = sorted(
            p
            for p in dossier_ec.rglob("*")
            if p.is_file() and p.suffix.lower() in {".csv", ".json"}
        )

    # Cas particulier : notre propre meta.json n'est pas une balance
    fichiers_ec = [p for p in fichiers_ec if not p.name.endswith(".meta.json")]

    if not fichiers_ec:
        print("-" * 78)
        print(" MODE VEILLE : aucune balance de l'expert-comptable disponible.")
        print(" Deposez sa balance (CSV 'compte;libelle;debit;credit' ou JSON)")
        print(f" dans : {dossier_ec}")
        print("=" * 78)
        return 4

    chemin_balance_ec = fichiers_ec[0]
    try:
        balance_ec = lire_balance_ec(chemin_balance_ec)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERREUR : balance EC illisible ({chemin_balance_ec}) : {exc}", file=sys.stderr)
        return 3

    print(f" Balance EC lue   : {chemin_balance_ec.name}  ({len(balance_ec)} comptes)")
    print(f" Tolerances       : {fmt(tolerance)} EUR")
    print("-" * 78)

    ecarts = comparer(notre_balance, balance_ec, tolerance)

    if not ecarts:
        print(" RESULTAT : aucun ecart significatif avec l'expert-comptable.")
        print("=" * 78)
        return 0

    print(f" ECARTS DETECTES : {len(ecarts)} compte(s)")
    print("-" * 78)
    entete = f" {'Compte':<10} {'Notre solde':>14} {'Solde EC':>14} {'Delta':>14}  Qualification"
    print(entete)
    for ecart in ecarts:
        print(
            f" {ecart['compte']:<10} "
            f"{fmt(Decimal(ecart['notre_solde'])):>14} "
            f"{fmt(Decimal(ecart['ec_solde'])):>14} "
            f"{fmt(Decimal(ecart['delta_solde'])):>14}  "
            f"{ecart['qualification']}"
        )
    print("=" * 78)

    if options.json:
        rapport = {
            "script": "comparer_avec_ec.py",
            "version": __version__,
            "execution": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "balance_ec": str(chemin_balance_ec),
            "tolerance": str(tolerance),
            "nb_ecarts": len(ecarts),
            "ecarts": ecarts,
        }
        print(json.dumps(rapport, indent=2, ensure_ascii=False))

    return 1


if __name__ == "__main__":
    sys.exit(main())
