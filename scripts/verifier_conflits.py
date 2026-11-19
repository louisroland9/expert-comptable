#!/usr/bin/env python3
"""Contrôle des marqueurs de conflit git (hook pre-commit).

Détecte toute ligne commençant strictement par sept chevrons ouvrants
(``<<<<<<<``) ou fermants (``>>>>>>>``), ainsi que le séparateur ``=======``
d'un conflit à trois voies.

Stdlib pure — aucun calcul monétaire, aucun `Decimal` requis ici.

Usage :
    python3 scripts/verifier_conflits.py [fichier ...]

Codes de sortie (règle R7/03) :
    0  aucun marqueur
    1  marqueurs détectés (avertissement bloquant pour le commit)
    3  erreur d'entrée (fichier illisible)
"""

from __future__ import annotations

import sys
from pathlib import Path

MARQUEURS = ("<<<<<<<", "=======", ">>>>>>>")


def analyser(chemin: Path) -> list[tuple[int, str]]:
    """Retourne la liste (numéro de ligne, marqueur) trouvée dans ``chemin``."""
    trouves: list[tuple[int, str]] = []
    try:
        contenu = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"⚠️  Lecture impossible : {chemin} ({exc})", file=sys.stderr)
        raise
    for numero, ligne in enumerate(contenu.splitlines(), start=1):
        for marqueur in MARQUEURS:
            if ligne.startswith(marqueur):
                # `=======` seul est ambigu (titres markdown) : on n'accepte
                # que la variante bordée de tirets d'un conflit réel.
                if marqueur == "=======" and ligne.strip() != "=======":
                    continue
                trouves.append((numero, marqueur))
                break
    return trouves


def main(argv: list[str] | None = None) -> int:
    fichiers = [Path(a) for a in (argv if argv is not None else sys.argv[1:])]
    if not fichiers:
        print("Aucun fichier à contrôler.")
        return 0

    erreur_entree = False
    total = 0
    for fichier in fichiers:
        if not fichier.is_file():
            continue
        try:
            trouves = analyser(fichier)
        except OSError:
            erreur_entree = True
            continue
        for numero, marqueur in trouves:
            print(f"🔴 {fichier}:{numero} — marqueur de conflit « {marqueur} »")
            total += 1

    if erreur_entree:
        return 3
    if total:
        print(
            f"\n{total} marqueur(s) de conflit détecté(s) : résous le conflit avant de committer."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
