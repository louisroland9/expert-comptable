#!/usr/bin/env python3
"""Calcul des amortissements et des écritures de reclassement — LR Data (SASU).

Lit le **registre des immobilisations** (tableau Markdown de
``memory-bank/immobilisations-et-charges.md``) et calcule, pour chaque bien :

  * la **dotation de l'exercice** en linéaire, avec **prorata temporis en jours**
    (``dotation = HT / duree_annees * jours_detenus / 365``) ;
  * les **écritures de reclassement** (charge -> immobilisation) si le bien a été
    initialement passé en charge (règle PCG stricte, décision D-09) ;
  * les **écritures de dotation** (``681100`` / ``281830``).

Convention d'amortissement (décision D-07)
------------------------------------------
  * Linéaire, durée **3 ans** (taux **33,33 %**) par défaut pour le matériel
    informatique ; surchargeable par bien dans le registre (colonne ``Durée``).
  * Prorata en **jours** sur 365, à partir de la date d'acquisition incluse.
  * Aucun calcul de tête : tout passe par ``decimal.Decimal``.

Entrées
-------
``--registre`` : chemin du fichier Markdown contenant le registre
(défaut : ``memory-bank/immobilisations-et-charges.md``).
Le registre est lu en **lecture seule** : il n'est jamais modifié.

Sorties
-------
``--sortie`` : répertoire de sortie (défaut : ``exports-fiscaux/journaux/``).
Produit ``journal_OD_amortissements_<exercice>.csv`` (reclassement + dotation),
**et uniquement si l'ensemble est équilibré**.

⚠️ Aucune écriture n'est produite si le registre est vide : le script sort avec
le code ``1`` (avertissement) et le signale explicitement.

Format du registre (tableau Markdown)
-------------------------------------
Le script cherche la ligne d'en-tête contenant ``Libellé`` et ``HT`` puis lit les
lignes suivantes (colonnes reconnues : Date, Libellé, Fournisseur, Facture, HT,
TVA, Durée, Compte). Une cellule ``—`` marque une ligne vide (ignorée).

Usage
-----
    python3 scripts/amortissements.py
    python3 scripts/amortissements.py --exercice 2026 --json
    python3 scripts/amortissements.py --registre chemin/registre.md --sortie /tmp/od

Codes de sortie
---------------
    0  calcul réalisé, écritures équilibrées (ou aucune écriture à produire)
    1  calcul réalisé avec avertissements (registre vide, bien ignoré)
    2  déséquilibre détecté -> aucune écriture écrite
    3  erreur d'entrée (registre absent, format invalide)
"""

from __future__ import annotations

import datetime as _dt
import re
import sys
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier_equilibre import (  # noqa: E402
    CENT,
    ZERO,
    Ecriture,
    Ligne,
    fmt,
)

__version__ = "1.0.0"

# Comptes PCG (cf. memory-bank/plan-comptable-sasu.md)
COMPTE_IMMO_MATERIEL = "218300"
LIBELLE_IMMO_MATERIEL = "Matériel de bureau et informatique"
COMPTE_CHARGE_MATERIEL = "606300"
LIBELLE_CHARGE_MATERIEL = "Fournitures informatiques"
COMPTE_DOTATION = "681100"
LIBELLE_DOTATION = "Dotations aux amortissements"
COMPTE_AMORT_MATERIEL = "281830"
LIBELLE_AMORT_MATERIEL = "Amort. matériel de bureau/informatique"

DUREE_DEFAUT_ANNEES = Decimal("3")
TAUX_DEFAUT = Decimal("0.3333")
JOURS_BASE = Decimal("365")
SEUIL_CHARGE = Decimal("500.00")


# --------------------------------------------------------------------------- #
# Structures
# --------------------------------------------------------------------------- #
@dataclass
class Bien:
    """Un bien immobilisable lu dans le registre."""

    rang: str
    date: str  # JJ/MM/AAAA
    libelle: str
    fournisseur: str
    facture: str
    ht: Decimal
    tva: Decimal
    duree_annees: Decimal
    compte_charge: str = COMPTE_CHARGE_MATERIEL

    @property
    def date_acquisition(self) -> _dt.date:
        return _dt.datetime.strptime(self.date, "%d/%m/%Y").date()

    def jours_detenus(self, date_cloture: _dt.date) -> int:
        debut = self.date_acquisition
        if debut > date_cloture:
            return 0
        return (date_cloture - debut).days + 1

    def dotation(self, date_cloture: _dt.date) -> Decimal:
        """Dotation linéaire prorata temporis, quantifiée au centime."""
        jours = self.jours_detenus(date_cloture)
        if jours <= 0 or self.duree_annees <= 0:
            return ZERO
        annuite = self.ht / self.duree_annees
        dotation = annuite * Decimal(jours) / JOURS_BASE
        return dotation.quantize(CENT, rounding=ROUND_HALF_UP)

    @property
    def taux(self) -> Decimal:
        if self.duree_annees <= 0:
            return ZERO
        return (Decimal("1") / self.duree_annees).quantize(Decimal("0.0001"))


@dataclass
class Anomalie:
    niveau: int  # 1 = avertissement, 2 = desequilibre, 3 = erreur d'entree
    message: str


@dataclass
class Resultat:
    exercice: int
    date_cloture: _dt.date
    biens: list[Bien] = field(default_factory=list)
    anomalies: list[Anomalie] = field(default_factory=list)
    ecritures: list[Ecriture] = field(default_factory=list)
    registre: Path | None = None

    @property
    def total_reclassement(self) -> Decimal:
        return sum((b.ht for b in self.biens), ZERO)

    @property
    def total_dotation(self) -> Decimal:
        return sum((b.dotation(self.date_cloture) for b in self.biens), ZERO)


# --------------------------------------------------------------------------- #
# Lecture du registre
# --------------------------------------------------------------------------- #
_MOTIF_PLACEHOLDER = re.compile(r"^[—\-–\s]*$")
_MOTIF_MONTANT = re.compile(r"[^0-9,.\-]")


def _nettoyer(cellule: str) -> str:
    return cellule.strip().replace("**", "").replace("`", "").strip()


def _est_placeholder(cellule: str) -> bool:
    return bool(_MOTIF_PLACEHOLDER.match(cellule)) or cellule in {"", "—", "-"}


def _parse_montant(cellule: str) -> Decimal:
    """Accepte ``1 200,00 €``, ``1,200.00``, ``1200`` ; retourne 0 si vide."""
    brut = _nettoyer(cellule)
    if _est_placeholder(brut):
        return ZERO
    brut = _MOTIF_MONTANT.sub("", brut.replace("€", "").replace(" ", ""))
    if not brut:
        return ZERO
    if "," in brut and "." in brut:
        brut = brut.replace(",", "")  # 1,200.00 -> 1200.00
    elif "," in brut:
        brut = brut.replace(",", ".")  # 1200,00 -> 1200.00
    try:
        return Decimal(brut).quantize(CENT, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValueError(f"montant illisible : {cellule!r}") from exc


def _parse_duree(cellule: str) -> Decimal:
    brut = _nettoyer(cellule).lower()
    if _est_placeholder(brut):
        return DUREE_DEFAUT_ANNEES
    nombre = re.search(r"\d+(?:[.,]\d+)?", brut)
    if not nombre:
        return DUREE_DEFAUT_ANNEES
    valeur = Decimal(nombre.group(0).replace(",", "."))
    if "mois" in brut:  # « 36 mois » -> 3 ans
        valeur = valeur / Decimal("12")
    return valeur.quantize(Decimal("0.01"))


def _parse_date(cellule: str) -> str:
    brut = _nettoyer(cellule)
    for motif in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return _dt.datetime.strptime(brut, motif).strftime("%d/%m/%Y")
        except ValueError:
            continue
    raise ValueError(f"date illisible : {cellule!r}")


def _colonnes(entete: list[str]) -> dict[str, int]:
    """Associe chaque colonne utile à son index (tolérant aux libellés)."""
    index: dict[str, int] = {}
    for i, cellule in enumerate(entete):
        libelle = _nettoyer(cellule).lower()
        if "libell" in libelle:
            index.setdefault("libelle", i)
        elif "fournisseur" in libelle:
            index.setdefault("fournisseur", i)
        elif "facture" in libelle or "pièce" in libelle or "piece" in libelle:
            index.setdefault("facture", i)
        elif "date" in libelle:
            index.setdefault("date", i)
        elif "durée" in libelle or "duree" in libelle:
            index.setdefault("duree", i)
        elif "tva" in libelle:
            index.setdefault("tva", i)
        elif libelle == "ht" or " ht" in libelle:
            index.setdefault("ht", i)
        elif "compte" in libelle:
            index.setdefault("compte", i)
    return index


def _decouper_ligne(ligne: str) -> list[str]:
    contenu = ligne.strip()
    if contenu.startswith("|"):
        contenu = contenu[1:]
    if contenu.endswith("|"):
        contenu = contenu[:-1]
    return [c.strip() for c in contenu.split("|")]


def lire_registre(chemin: Path) -> tuple[list[Bien], list[Anomalie]]:
    """Lit le tableau Markdown du registre ; retourne les biens et les anomalies."""
    biens: list[Bien] = []
    anomalies: list[Anomalie] = []
    if not chemin.exists():
        raise FileNotFoundError(f"registre introuvable : {chemin}")

    lignes = chemin.read_text(encoding="utf-8").splitlines()

    # 1) Trouver la ligne d'en-tête du registre
    debut = None
    for i, ligne in enumerate(lignes):
        if not ligne.lstrip().startswith("|"):
            continue
        textes = [_nettoyer(c).lower() for c in _decouper_ligne(ligne)]
        if any("libell" in t for t in textes) and any(t == "ht" for t in textes):
            debut = i
            break
    if debut is None:
        anomalies.append(Anomalie(1, "Aucun tableau « registre » (en-tête Libellé/HT) trouvé."))
        return biens, anomalies

    entete = _decouper_ligne(lignes[debut])
    index = _colonnes(entete)
    manquants = {"libelle", "date", "ht"} - set(index)
    if manquants:
        raise ValueError(
            f"colonnes obligatoires absentes du registre : {', '.join(sorted(manquants))}"
        )

    # 2) Lire les lignes de données jusqu'à la fin du tableau
    for offset, ligne in enumerate(lignes[debut + 1 :], start=1):
        if not ligne.lstrip().startswith("|"):
            break
        cellules = _decouper_ligne(ligne)
        if all(set(c) <= set("-: ") for c in cellules):
            continue  # ligne de séparation Markdown
        if len(cellules) < len(entete):
            cellules += [""] * (len(entete) - len(cellules))

        def cellule(nom: str, _c: list[str] = cellules) -> str:
            i = index.get(nom)
            return _c[i] if i is not None and i < len(_c) else ""

        libelle = _nettoyer(cellule("libelle"))
        if _est_placeholder(libelle):
            continue  # ligne vide du registre

        try:
            ht = _parse_montant(cellule("ht"))
            date = _parse_date(cellule("date"))
        except ValueError as exc:
            anomalies.append(Anomalie(1, f"Bien ignoré ({exc}) — ligne {debut + offset + 2}"))
            continue

        if ht <= ZERO:
            anomalies.append(Anomalie(1, f"Bien ignoré « {libelle} » : montant HT nul ou absent."))
            continue
        if ht <= SEUIL_CHARGE:
            anomalies.append(
                Anomalie(
                    1,
                    f"Bien « {libelle} » ({fmt(ht)} € HT) ≤ 500 € HT : reste en charge, "
                    "aucun reclassement.",
                )
            )
            continue

        compte = _nettoyer(cellule("compte"))
        biens.append(
            Bien(
                rang=_nettoyer(cellule("rang")) or str(len(biens) + 1),
                date=date,
                libelle=libelle,
                fournisseur=_nettoyer(cellule("fournisseur")),
                facture=_nettoyer(cellule("facture")),
                ht=ht,
                tva=_parse_montant(cellule("tva")),
                duree_annees=_parse_duree(cellule("duree")),
                compte_charge=compte if compte.startswith("606") else COMPTE_CHARGE_MATERIEL,
            )
        )

    return biens, anomalies


# --------------------------------------------------------------------------- #
# Construction des écritures
# --------------------------------------------------------------------------- #
def construire_ecritures(resultat: Resultat) -> list[Ecriture]:
    """Construit les écritures de reclassement puis de dotation, bien par bien."""
    ecritures: list[Ecriture] = []
    date_od = resultat.date_cloture.strftime("%d/%m/%Y")
    compteur = 0

    for bien in resultat.biens:
        # a) Reclassement charge -> immobilisation
        compteur += 1
        piece = bien.facture or f"OD-{resultat.exercice}-{compteur:03d}"
        ecritures.append(
            Ecriture(
                date=date_od,
                libelle=f"Reclassement {bien.libelle} — facture {piece}",
                numero=f"OD-{resultat.exercice}-{compteur:03d}",
                piece=piece,
                lignes=[
                    Ligne(
                        compte=COMPTE_IMMO_MATERIEL,
                        libelle=LIBELLE_IMMO_MATERIEL,
                        debit=bien.ht,
                        credit=ZERO,
                        source="amortissements.py",
                    ),
                    Ligne(
                        compte=bien.compte_charge,
                        libelle=LIBELLE_CHARGE_MATERIEL,
                        debit=ZERO,
                        credit=bien.ht,
                        source="amortissements.py",
                    ),
                ],
            )
        )

        # b) Dotation aux amortissements
        dotation = bien.dotation(resultat.date_cloture)
        if dotation > ZERO:
            compteur += 1
            ecritures.append(
                Ecriture(
                    date=date_od,
                    libelle=f"Dotation {resultat.exercice} — {bien.libelle}",
                    numero=f"OD-{resultat.exercice}-{compteur:03d}",
                    piece=f"OD-{resultat.exercice}-{compteur:03d}",
                    lignes=[
                        Ligne(
                            compte=COMPTE_DOTATION,
                            libelle=LIBELLE_DOTATION,
                            debit=dotation,
                            credit=ZERO,
                            source="amortissements.py",
                        ),
                        Ligne(
                            compte=COMPTE_AMORT_MATERIEL,
                            libelle=LIBELLE_AMORT_MATERIEL,
                            debit=ZERO,
                            credit=dotation,
                            source="amortissements.py",
                        ),
                    ],
                )
            )

    return ecritures
