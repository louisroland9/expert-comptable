#!/usr/bin/env python3
"""Contrôle d'équilibre et de structure des journaux comptables — LR Data (SASU).

Vérifie, pour un répertoire de journaux, que :
  1. chaque écriture est équilibrée  (Σ Débit == Σ Crédit) ;
  2. chaque journal  est équilibré   (Σ Débit == Σ Crédit) ;
  3. le jeu complet  est équilibré   (Σ Débit == Σ Crédit) ;
  4. la structure des enregistrements est valide (comptes PCG, sens, montants).

Aucune dépendance externe : uniquement la bibliothèque standard (Decimal, json, csv).

Formats d'entrée acceptés
-------------------------
A) JSON natif (format de travail du harnais) ::

    {
      "journal": "AC",
      "periode": "2026-11",
      "ecritures": [
        {
          "date": "2026-11-05",
          "libelle": "Facture Qonto abonnement",
          "piece": "FAC-2026-11-001",
          "lignes": [
            {"compte": "627800", "libelle": "Services bancaires", "debit": "12.90", "credit": "0.00"},
            {"compte": "445660", "libelle": "TVA deductible",     "debit": "2.58",  "credit": "0.00"},
            {"compte": "401000", "libelle": "Fournisseurs",       "debit": "0.00",  "credit": "15.48"}
          ]
        }
      ]
    }

B) CSV d'écritures (une ligne par ligne d'écriture) avec en-tête :

    journal,date,ecriture_num,compte,libelle,debit,credit,piece
    AC,05/11/2026,1,627800,Services bancaires,12.90,0.00,FAC-001

Les montants peuvent être écrits avec un point ou une virgule décimale.

Usage
-----
    python3 scripts/verifier_equilibre.py                 # exporte exports-fiscaux/
    python3 scripts/verifier_equilibre.py --dir <chemin>  # autre répertoire
    python3 scripts/verifier_equilibre.py --json          # sortie JSON machine

Codes de sortie
---------------
    0  succès, équilibre vérifié
    1  succès technique mais anomalies detectees (avertissements)
    2  desequilibre ou erreur de structure
    3  erreur d'entree (fichier manquant, JSON/CSV invalide)
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

__version__ = "1.0.0"

ZERO = Decimal("0.00")
CENT = Decimal("0.01")
COMPTE_RE = re.compile(r"^\d{3,8}$")
TAUX_ANOMALIE = {"1": "anomalie", "2": "desequilibre", "3": "erreur"}


# --------------------------------------------------------------------------- #
# Utilitaires monétaires
# --------------------------------------------------------------------------- #
def parse_montant(valeur: Any) -> Decimal:
    """Convertit un montant (str, int, float, None) en Decimal quantifié.

    Accepte les séparateurs français (virgule), les espaces insécables et un
    éventuel symbole euro. Ne tolère aucun arrondi silencieux : la valeur est
    quantifiée à 2 décimales en ROUND_HALF_UP.
    """
    if valeur is None:
        return ZERO
    if isinstance(valeur, Decimal):
        return valeur.quantize(CENT)
    if isinstance(valeur, int):
        return Decimal(valeur).quantize(CENT)
    if isinstance(valeur, float):
        # Les flottants ne doivent pas entrer dans un flux monétaire : on
        # passe par une repr textuelle pour éviter les artefacts binaires.
        return Decimal(repr(valeur)).quantize(CENT)

    texte = str(valeur).strip()
    if texte == "":
        return ZERO
    texte = texte.replace("\u202f", "").replace("\xa0", "").replace(" ", "")
    texte = texte.replace("€", "").replace("EUR", "").strip()
    if "," in texte and "." in texte:
        # 1.234,56 -> 1234.56
        texte = texte.replace(".", "").replace(",", ".")
    else:
        texte = texte.replace(",", ".")
    try:
        return Decimal(texte).quantize(CENT)
    except InvalidOperation as exc:
        raise ValueError(f"Montant illisible : {valeur!r}") from exc


def fmt(montant: Decimal) -> str:
    """Affichage français à 2 décimales (virgule décimale)."""
    return f"{montant:,.2f}".replace(",", " ").replace(".", ",")


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


class LecteurErreur(Exception):
    """Erreur d'entree (fichier absent ou illisible)."""


# --------------------------------------------------------------------------- #
# Modèle de données
# --------------------------------------------------------------------------- #
@dataclass
class Ligne:
    compte: str
    libelle: str
    debit: Decimal
    credit: Decimal
    source: str = ""

    @property
    def montant(self) -> Decimal:
        return self.debit if self.debit > ZERO else self.credit

    def sens(self) -> str:
        if self.debit > ZERO and self.credit > ZERO:
            return "AMBIGU"
        if self.debit > ZERO:
            return "D"
        if self.credit > ZERO:
            return "C"
        return "NUL"


@dataclass
class Ecriture:
    date: str
    libelle: str
    numero: str
    piece: str
    lignes: list[Ligne] = field(default_factory=list)

    @property
    def total_debit(self) -> Decimal:
        return sum((l.debit for l in self.lignes), ZERO)

    @property
    def total_credit(self) -> Decimal:
        return sum((l.credit for l in self.lignes), ZERO)

    @property
    def ecart(self) -> Decimal:
        return (self.total_debit - self.total_credit).quantize(CENT)

    @property
    def equilibre(self) -> bool:
        return self.ecart == ZERO


@dataclass
class Journal:
    code: str
    source: Path
    ecritures: list[Ecriture] = field(default_factory=list)

    @property
    def total_debit(self) -> Decimal:
        return sum((e.total_debit for e in self.ecritures), ZERO)

    @property
    def total_credit(self) -> Decimal:
        return sum((e.total_credit for e in self.ecritures), ZERO)

    @property
    def ecart(self) -> Decimal:
        return (self.total_debit - self.total_credit).quantize(CENT)

    @property
    def equilibre(self) -> bool:
        return self.ecart == ZERO


@dataclass
class Anomalie:
    niveau: int  # 1 = avertissement, 2 = desequilibre, 3 = erreur d'entree
    source: str
    message: str


# --------------------------------------------------------------------------- #
# Chargement des journaux
# --------------------------------------------------------------------------- #
def lister_fichiers(racine: Path) -> list[Path]:
    """Fichiers de journaux reconnus, par ordre stable.

    Les fichiers de tracabilite ``*.meta.json`` produits par les scripts sont
    ignores pour ne pas etre interpretes comme des journaux.
    """
    fichiers: list[Path] = []
    for motif in ("*.json", "*.csv"):
        fichiers.extend(sorted(p for p in racine.rglob(motif) if p.is_file()))
    return [p for p in fichiers if not p.name.endswith(".meta.json")]


def _extraire_ecritures_json(doc: Any, source: Path) -> tuple[str, list[Ecriture]]:
    """Construit le journal a partir d'un document JSON."""
    if isinstance(doc, list):
        code = source.stem.upper()
        ecritures_brutes = doc
    elif isinstance(doc, dict):
        code = str(doc.get("journal") or source.stem.upper())
        if "ecritures" in doc:
            ecritures_brutes = doc["ecritures"]
        elif "lignes" in doc:
            ecritures_brutes = [doc]
        else:
            raise LecteurErreur("JSON sans cle 'ecritures' ni 'lignes'")
    else:
        raise LecteurErreur("JSON de type inattendu (ni objet ni tableau)")

    if not isinstance(ecritures_brutes, list):
        raise LecteurErreur("'ecritures' doit etre un tableau")

    ecritures: list[Ecriture] = []
    for index, item in enumerate(ecritures_brutes, start=1):
        if not isinstance(item, dict) or "lignes" not in item:
            raise LecteurErreur(f"ecriture #{index} sans cle 'lignes'")
        lignes: list[Ligne] = []
        for brute in item["lignes"]:
            try:
                debit = parse_montant(brute.get("debit"))
                credit = parse_montant(brute.get("credit"))
            except ValueError as exc:
                raise LecteurErreur(f"ecriture #{index} : {exc}") from exc
            lignes.append(
                Ligne(
                    compte=str(brute.get("compte", "")).strip(),
                    libelle=str(brute.get("libelle", "")).strip(),
                    debit=debit,
                    credit=credit,
                    source=f"{source.name}#{index}",
                )
            )
        ecritures.append(
            Ecriture(
                date=str(item.get("date", "")).strip(),
                libelle=str(item.get("libelle", "")).strip(),
                numero=str(item.get("numero", index)).strip(),
                piece=str(item.get("piece", "")).strip(),
                lignes=lignes,
            )
        )
    return code.upper(), ecritures


def _extraire_ecritures_csv(contenu: str, source: Path) -> dict[str, list[Ecriture]]:
    """Construit les journaux a partir d'un CSV (une ligne par ligne d'ecriture).

    Le CSV peut contenir plusieurs journaux (colonne ``journal``). Un dictionnaire
    ``{code_journal: [ecritures]}`` est retourne.
    """
    lecteur = csv.DictReader(io.StringIO(contenu))
    if not lecteur.fieldnames:
        raise LecteurErreur("CSV sans ligne d'en-tete")

    champs = {c.strip().lower() for c in lecteur.fieldnames if c}
    if "compte" not in champs:
        raise LecteurErreur("CSV sans colonne obligatoire 'compte'")

    groupes: dict[tuple[str, str, str], list[Ligne]] = {}
    meta: dict[tuple[str, str, str], dict[str, str]] = {}

    for numero_ligne, ligne_brute in enumerate(lecteur, start=2):
        normalisee = {(k or "").strip().lower(): (v or "") for k, v in ligne_brute.items()}
        journal = normalisee.get("journal", "").strip().upper() or source.stem.upper()
        date = normalisee.get("date", "").strip()
        numero = normalisee.get("ecriture_num", "").strip() or normalisee.get("numero", "").strip()
        cle = (journal, date, numero or str(numero_ligne))
        try:
            debit = parse_montant(normalisee.get("debit"))
            credit = parse_montant(normalisee.get("credit"))
        except ValueError as exc:
            raise LecteurErreur(f"ligne {numero_ligne} : {exc}") from exc
        groupes.setdefault(cle, []).append(
            Ligne(
                compte=normalisee.get("compte", "").strip(),
                libelle=normalisee.get("libelle", "").strip(),
                debit=debit,
                credit=credit,
                source=f"{source.name}:{numero_ligne}",
            )
        )
        meta.setdefault(
            cle,
            {
                "libelle": normalisee.get("libelle_ecriture", "").strip(),
                "piece": normalisee.get("piece", "").strip(),
            },
        )

    resultat: dict[str, list[Ecriture]] = {}
    for cle in sorted(groupes):
        journal, date, numero = cle
        lignes = groupes[cle]
        infos = meta.get(cle, {})
        resultat.setdefault(journal, []).append(
            Ecriture(
                date=date,
                libelle=infos.get("libelle", "") or (lignes[0].libelle if lignes else ""),
                numero=numero,
                piece=infos.get("piece", ""),
                lignes=lignes,
            )
        )
    return resultat


def charger_journaux(chemin: Path) -> list[Journal]:
    """Charge un ou plusieurs journaux depuis un fichier JSON ou CSV.

    Un JSON correspond a un seul journal ; un CSV peut en contenir plusieurs
    (colonne ``journal``).
    """
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as exc:
        raise LecteurErreur(f"lecture impossible : {exc}") from exc

    suffixe = chemin.suffix.lower()
    if suffixe == ".json":
        try:
            document = json.loads(texte)
        except json.JSONDecodeError as exc:
            raise LecteurErreur(f"JSON invalide : {exc}") from exc
        code, ecritures = _extraire_ecritures_json(document, chemin)
        return [Journal(code=code, source=chemin, ecritures=ecritures)]
    if suffixe == ".csv":
        journaux: list[Journal] = []
        for code, ecritures in sorted(_extraire_ecritures_csv(texte, chemin).items()):
            journaux.append(Journal(code=code, source=chemin, ecritures=ecritures))
        return journaux
    raise LecteurErreur(f"extension non supportee : {chemin.suffix}")


# --------------------------------------------------------------------------- #
# Contrôles
# --------------------------------------------------------------------------- #
def controler_journal(journal: Journal) -> list[Anomalie]:
    """Contrôles structurels et d'equilibre d'un journal."""
    anomalies: list[Anomalie] = []
    reference = str(journal.source)

    if not journal.ecritures:
        anomalies.append(Anomalie(1, reference, "journal sans aucune ecriture"))
        return anomalies

    for index, ecriture in enumerate(journal.ecritures, start=1):
        etiquette = f"{reference} -> ecriture #{index} ({ecriture.numero})"

        if not ecriture.lignes:
            anomalies.append(Anomalie(2, etiquette, "ecriture sans ligne"))
            continue

        if len(ecriture.lignes) < 2:
            anomalies.append(Anomalie(2, etiquette, "ecriture a moins de 2 lignes"))

        if not ecriture.date:
            anomalies.append(Anomalie(1, etiquette, "date manquante"))
        elif not re.match(r"^(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})$", ecriture.date):
            anomalies.append(
                Anomalie(1, etiquette, f"date au format inattendu : {ecriture.date!r}")
            )

        if not ecriture.equilibre:
            anomalies.append(
                Anomalie(
                    2,
                    etiquette,
                    f"deséquilibre : débit {fmt(ecriture.total_debit)} "
                    f"!= crédit {fmt(ecriture.total_credit)} (écart {fmt(ecriture.ecart)})",
                )
            )

        for ligne in ecriture.lignes:
            etiquette_ligne = f"{etiquette} -> compte {ligne.compte or '(vide)'}"

            if not ligne.compte:
                anomalies.append(Anomalie(2, etiquette_ligne, "compte manquant"))
            elif not COMPTE_RE.match(ligne.compte):
                anomalies.append(
                    Anomalie(2, etiquette_ligne, f"numéro de compte invalide : {ligne.compte!r}")
                )

            sens = ligne.sens()
            if sens == "AMBIGU":
                anomalies.append(
                    Anomalie(2, etiquette_ligne, "ligne à la fois au débit et au crédit")
                )
            elif sens == "NUL":
                anomalies.append(
                    Anomalie(1, etiquette_ligne, "ligne sans montant (débit = crédit = 0)")
                )

            if not ligne.libelle:
                anomalies.append(Anomalie(1, etiquette_ligne, "libellé de ligne vide"))

        if not ecriture.piece:
            anomalies.append(Anomalie(1, etiquette, "aucune pièce justificative référencée"))

    return anomalies


def controler_ensemble(journaux: Iterable[Journal]) -> list[Anomalie]:
    """Contrôles transverses sur l'ensemble des journaux."""
    anomalies: list[Anomalie] = []
    journaux = list(journaux)

    for journal in journaux:
        if not journal.equilibre:
            anomalies.append(
                Anomalie(
                    2,
                    str(journal.source),
                    f"journal {journal.code} déséquilibré : débit {fmt(journal.total_debit)} "
                    f"!= crédit {fmt(journal.total_credit)} (écart {fmt(journal.ecart)})",
                )
            )

    total_debit = sum((j.total_debit for j in journaux), ZERO)
    total_credit = sum((j.total_credit for j in journaux), ZERO)
    ecart = (total_debit - total_credit).quantize(CENT)
    if ecart != ZERO:
        anomalies.append(
            Anomalie(
                2,
                "(ensemble)",
                f"jeu complet déséquilibré : débit {fmt(total_debit)} "
                f"!= crédit {fmt(total_credit)} (écart {fmt(ecart)})",
            )
        )

    codes: dict[str, list[str]] = {}
    for journal in journaux:
        codes.setdefault(journal.code, []).append(str(journal.source))
    for code, sources in sorted(codes.items()):
        if len(sources) > 1:
            anomalies.append(
                Anomalie(
                    1,
                    ", ".join(sources),
                    f"plusieurs fichiers pour le journal {code} "
                    "(vérifier l'absence de double comptage)",
                )
            )

    return anomalies


# --------------------------------------------------------------------------- #
# Rapport
# --------------------------------------------------------------------------- #
def construire_rapport(journaux: list[Journal], anomalies: list[Anomalie], racine: Path) -> dict:
    total_debit = sum((j.total_debit for j in journaux), ZERO)
    total_credit = sum((j.total_credit for j in journaux), ZERO)
    nb_ecritures = sum(len(j.ecritures) for j in journaux)
    nb_lignes = sum(len(e.lignes) for j in journaux for e in j.ecritures)
    return {
        "script": "verifier_equilibre.py",
        "version": __version__,
        "execution": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "racine": str(racine),
        "nb_journaux": len(journaux),
        "nb_ecritures": nb_ecritures,
        "nb_lignes": nb_lignes,
        "total_debit": str(total_debit),
        "total_credit": str(total_credit),
        "ecart": str((total_debit - total_credit).quantize(CENT)),
        "equilibre": (total_debit - total_credit).quantize(CENT) == ZERO,
        "journaux": [
            {
                "code": j.code,
                "fichier": str(j.source),
                "sha256": sha256_fichier(j.source) if j.source.is_file() else None,
                "nb_ecritures": len(j.ecritures),
                "total_debit": str(j.total_debit),
                "total_credit": str(j.total_credit),
                "ecart": str(j.ecart),
                "equilibre": j.equilibre,
            }
            for j in journaux
        ],
        "anomalies": [
            {
                "niveau": a.niveau,
                "qualification": TAUX_ANOMALIE.get(str(a.niveau), "?"),
                "source": a.source,
                "message": a.message,
            }
            for a in anomalies
        ],
        "nb_anomalies": len(anomalies),
    }


def afficher_rapport(rapport: dict) -> None:
    print("=" * 78)
    print(" CONTROLE D'EQUILIBRE ET DE STRUCTURE - LR Data (SASU)")
    print("=" * 78)
    print(f" Racine          : {rapport['racine']}")
    print(f" Execution       : {rapport['execution']}")
    print(f" Journaux        : {rapport['nb_journaux']}")
    print(f" Ecritures       : {rapport['nb_ecritures']}")
    print(f" Lignes          : {rapport['nb_lignes']}")
    print("-" * 78)
    if rapport["journaux"]:
        entete = f" {'Code':<6} {'Ecr.':>5} {'Total debit':>16} {'Total credit':>16} {'Ecart':>12}  Etat"
        print(entete)
        for j in rapport["journaux"]:
            etat = "OK" if j["equilibre"] else "DESEQUILIBRE"
            print(
                f" {j['code']:<6} {j['nb_ecritures']:>5} "
                f"{fmt(Decimal(j['total_debit'])):>16} "
                f"{fmt(Decimal(j['total_credit'])):>16} "
                f"{fmt(Decimal(j['ecart'])):>12}  {etat}"
            )
    else:
        print(" (aucun journal trouve)")
    print("-" * 78)
    print(
        f" TOTAL GENERAL   debit {fmt(Decimal(rapport['total_debit']))}  |  "
        f"credit {fmt(Decimal(rapport['total_credit']))}  |  "
        f"ecart {fmt(Decimal(rapport['ecart']))}"
    )
    print(f" Equilibre global : {'OUI' if rapport['equilibre'] else 'NON'}")
    print("-" * 78)

    anomalies = rapport["anomalies"]
    if not anomalies:
        print(" Anomalies : aucune")
    else:
        niveaux = {1: "AVERTISSEMENT", 2: "DESEQUILIBRE", 3: "ERREUR"}
        print(f" Anomalies : {len(anomalies)}")
        for anomalie in anomalies:
            print(f"  [{niveaux.get(anomalie['niveau'], '?')}] {anomalie['source']}")
            print(f"      {anomalie['message']}")
    print("=" * 78)


def ecrire_meta(rapport: dict, dossier_sortie: Path) -> Path:
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    horodatage = _dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")
    chemin = dossier_sortie / f"controle_equilibre_{horodatage}.meta.json"
    chemin.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")
    return chemin


# --------------------------------------------------------------------------- #
# Point d'entrée
# --------------------------------------------------------------------------- #
def resoudre_racine(demande: str | None) -> Path:
    if demande:
        return Path(demande).expanduser().resolve()
    projet = Path(__file__).resolve().parent.parent
    par_defaut = projet / "exports-fiscaux"
    return par_defaut if par_defaut.exists() else projet


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Controle d'equilibre et de structure des journaux comptables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    analyseur.add_argument("--dir", dest="racine", default=None,
                           help="repertoire contenant les journaux (defaut : exports-fiscaux/)")
    analyseur.add_argument("--json", action="store_true",
                           help="sortie JSON (machine) au lieu du rapport lisible")
    analyseur.add_argument("--meta", action="store_true",
                           help="ecrit un fichier .meta.json de tracabilite")
    analyseur.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    options = analyseur.parse_args(argv)

    racine = resoudre_racine(options.racine)
    if not racine.exists():
        message = f"Repertoire introuvable : {racine}"
        if options.json:
            print(json.dumps({"erreur": message, "code": 3}, ensure_ascii=False))
        else:
            print(f"ERREUR : {message}", file=sys.stderr)
        return 3

    anomalies: list[Anomalie] = []
    journaux: list[Journal] = []
    for fichier in lister_fichiers(racine):
        try:
            journaux_fichier = charger_journaux(fichier)
        except LecteurErreur as exc:
            anomalies.append(Anomalie(3, str(fichier), str(exc)))
            continue
        for journal in journaux_fichier:
            anomalies.extend(controler_journal(journal))
            journaux.append(journal)

    anomalies.extend(controler_ensemble(journaux))
    rapport = construire_rapport(journaux, anomalies, racine)

    if options.json:
        print(json.dumps(rapport, indent=2, ensure_ascii=False))
    else:
        afficher_rapport(rapport)

    if options.meta:
        chemin = ecrire_meta(rapport, racine.parent / "exports-fiscaux")
        if not options.json:
            print(f" Tracabilite ecrite : {chemin}")

    if any(a.niveau == 3 for a in anomalies):
        return 3
    if not rapport["equilibre"] or any(a.niveau == 2 for a in anomalies):
        return 2
    if anomalies:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
