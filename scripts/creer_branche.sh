#!/usr/bin/env bash
# =====================================================================
# LR Data — création d'une branche de travail
# =====================================================================
# Usage :
#   scripts/creer_branche.sh feat calcul-tva
#   scripts/creer_branche.sh fix equilibre-od
#   scripts/creer_branche.sh chore outillage-git
#   scripts/creer_branche.sh docs readme-racine
#
# Règle : UNE feature = UNE branche, créée depuis `main` à jour.
# Convention : feat/<slug> · fix/<slug> · chore/<slug> · docs/<slug>
# Le script NE pousse JAMAIS : le push est fait par l'utilisateur.
# =====================================================================

set -euo pipefail

PREFIXES_AUTORISES=("feat" "fix" "chore" "docs")
BRANCHE_PRINCIPALE="main"

rouge()  { printf '\033[31m%s\033[0m\n' "$*" >&2; }
jaune()  { printf '\033[33m%s\033[0m\n' "$*" >&2; }
vert()   { printf '\033[32m%s\033[0m\n' "$*"; }

if [ "$#" -ne 2 ]; then
  rouge "Usage : scripts/creer_branche.sh <feat|fix|chore|docs> <slug>"
  rouge "Exemple : scripts/creer_branche.sh feat calcul-tva"
  exit 3
fi

PREFIXE="$1"
SLUG="$2"

# --- 1. Préfixe autorisé ? -------------------------------------------
prefixe_valide=0
for p in "${PREFIXES_AUTORISES[@]}"; do
  [ "$PREFIXE" = "$p" ] && prefixe_valide=1
done
if [ "$prefixe_valide" -ne 1 ]; then
  rouge "Préfixe '$PREFIXE' refusé. Autorisés : ${PREFIXES_AUTORISES[*]}"
  exit 3
fi

# --- 2. Normalisation du slug ----------------------------------------
# minuscules, accents retirés, tout sauf [a-z0-9] -> tiret, tirets doublés réduits
SLUG_NORM="$(printf '%s' "$SLUG" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -e 's/à/à/g; s/é/e/g; s/è/e/g; s/ê/e/g; s/ë/e/g; s/á/a/g; s/â/a/g; s/ä/a/g; s/î/i/g; s/ï/i/g; s/ô/o/g; s/ö/o/g; s/ù/u/g; s/û/u/g; s/ü/u/g; s/ç/c/g' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g')"

if [ -z "$SLUG_NORM" ]; then
  rouge "Slug '$SLUG' invalide : aucun caractère exploitable."
  exit 3
fi
if [ "$SLUG_NORM" != "$SLUG" ]; then
  jaune "Slug normalisé : '$SLUG' -> '$SLUG_NORM'"
fi

BRANCHE="$PREFIXE/$SLUG_NORM"

# --- 3. Dépôt git ? ---------------------------------------------------
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  rouge "Ce répertoire n'est pas un dépôt git."
  exit 3
fi

# --- 4. Arbre de travail propre ? ------------------------------------
if [ -n "$(git status --porcelain)" ]; then
  rouge "Arbre de travail sale : committe ou remise à zéro avant de créer une branche."
  rouge "  git status"
  exit 1
fi

# --- 5. La branche n'existe pas déjà ? -------------------------------
if git show-ref --verify --quiet "refs/heads/$BRANCHE"; then
  rouge "La branche locale '$BRANCHE' existe déjà."
  rouge "  git switch $BRANCHE"
  exit 1
fi

# --- 6. Retour sur main à jour ---------------------------------------
COURANTE="$(git branch --show-current)"
if [ "$COURANTE" != "$BRANCHE_PRINCIPALE" ]; then
  jaune "Branche courante '$COURANTE' -> retour sur '$BRANCHE_PRINCIPALE'."
  git switch "$BRANCHE_PRINCIPALE"
fi

git fetch --quiet origin "$BRANCHE_PRINCIPALE" 2>/dev/null || jaune "fetch impossible (hors ligne ?) : on part de l'état local."

if git rev-parse --verify --quiet "origin/$BRANCHE_PRINCIPALE" >/dev/null; then
  if [ "$(git rev-list --count "HEAD..origin/$BRANCHE_PRINCIPALE")" -gt 0 ]; then
    jaune "Attention : 'origin/$BRANCHE_PRINCIPALE' contient des commits non présents localement."
    jaune "  git pull --ff-only"
  fi
fi

# --- 7. Création ------------------------------------------------------
git switch --create "$BRANCHE"

vert "Branche '$BRANCHE' créée depuis '$BRANCHE_PRINCIPALE'."
vert "Prochaines étapes :"
tree_etapes="  1. modifier / créer les fichiers
  2. git add -p            (découpage atomique)
  3. git commit            (Conventional Commits, validé par cz check)
  4. git push -u origin $BRANCHE   <-- À FAIRE PAR L'UTILISATEUR"
vert "$tree_etapes"
