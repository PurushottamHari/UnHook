#!/usr/bin/env bash
# ============================================================
# copy_generated_folders.sh
#
# Finds all 'generated' folders within downloads/railway/<timestamp>/
# and copies them to downloads/prompts/<timestamp>/ while preserving
# the directory structure.
#
# Usage:
#   ./scripts/copy_generated_folders.sh
#   ./scripts/copy_generated_folders.sh --dry-run
# ============================================================

set -euo pipefail

# --------------- colours & helpers --------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}ℹ  $*${RESET}"; }
success() { echo -e "${GREEN}✅ $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${RESET}"; }
error()   { echo -e "${RED}❌ $*${RESET}" >&2; exit 1; }
step()    { echo -e "\n${BOLD}── $* ──${RESET}"; }

# --------------- dry-run flag --------------------------------
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  warn "DRY RUN – no files will be copied"
fi

# --------------- configuration ------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAILWAY_DOWNLOADS_BASE="${REPO_ROOT}/downloads/railway"
PROMPTS_BASE="${REPO_ROOT}/downloads/prompts"

# --------------- sanity checks ------------------------------
step "Pre-flight checks"

if [[ ! -d "${RAILWAY_DOWNLOADS_BASE}" ]]; then
  error "Railway downloads directory not found: ${RAILWAY_DOWNLOADS_BASE}"
fi

# --------------- find timestamp directories ------------------
step "Finding timestamp directories in ${RAILWAY_DOWNLOADS_BASE}"

TIMESTAMP_DIRS=()
while IFS= read -r -d '' dir; do
  TIMESTAMP_DIRS+=("${dir}")
done < <(find "${RAILWAY_DOWNLOADS_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if [[ ${#TIMESTAMP_DIRS[@]} -eq 0 ]]; then
  error "No timestamp directories found in ${RAILWAY_DOWNLOADS_BASE}"
fi

info "Found ${#TIMESTAMP_DIRS[@]} timestamp directory/directories"

# --------------- process each timestamp ---------------------
TOTAL_COPIED=0
TOTAL_GENERATED=0

for timestamp_dir in "${TIMESTAMP_DIRS[@]}"; do
  TIMESTAMP="$(basename "${timestamp_dir}")"
  step "Processing timestamp: ${TIMESTAMP}"

  # Find all 'generated' directories within this timestamp
  GENERATED_DIRS=()
  while IFS= read -r -d '' dir; do
    GENERATED_DIRS+=("${dir}")
  done < <(find "${timestamp_dir}" -type d -name "generated" -print0)

  if [[ ${#GENERATED_DIRS[@]} -eq 0 ]]; then
    warn "No 'generated' folders found for timestamp ${TIMESTAMP}"
    continue
  fi

  info "Found ${#GENERATED_DIRS[@]} 'generated' folder(s)"
  TOTAL_GENERATED=$(( TOTAL_GENERATED + ${#GENERATED_DIRS[@]} ))

  # Create destination directory
  PROMPTS_DEST="${PROMPTS_BASE}/${TIMESTAMP}"
  if [[ "${DRY_RUN}" == "false" ]]; then
    mkdir -p "${PROMPTS_DEST}"
  else
    info "[dry-run] would mkdir -p '${PROMPTS_DEST}'"
  fi

  # Copy each generated folder preserving structure
  for generated_dir in "${GENERATED_DIRS[@]}"; do
    # Get the relative path from the timestamp directory
    rel_path="${generated_dir#${timestamp_dir}/}"
    
    # Destination path
    dest_path="${PROMPTS_DEST}/${rel_path}"
    
    info "Copying: ${rel_path}"
    
    if [[ "${DRY_RUN}" == "false" ]]; then
      # Create parent directory if needed
      mkdir -p "$(dirname "${dest_path}")"
      # Copy the directory recursively
      cp -r "${generated_dir}" "${dest_path}"
      TOTAL_COPIED=$(( TOTAL_COPIED + 1 ))
    else
      info "[dry-run] would cp -r '${generated_dir}' '${dest_path}'"
      TOTAL_COPIED=$(( TOTAL_COPIED + 1 ))
    fi
  done

  success "Copied ${#GENERATED_DIRS[@]} generated folder(s) to ${PROMPTS_DEST}"
done

# --------------- summary ------------------------------------
step "Summary"
echo -e "  Source base: ${BOLD}${RAILWAY_DOWNLOADS_BASE}${RESET}"
echo -e "  Dest base  : ${BOLD}${PROMPTS_BASE}${RESET}"
echo -e "  Total generated folders found: ${BOLD}${TOTAL_GENERATED}${RESET}"
echo -e "  Total folders copied: ${BOLD}${TOTAL_COPIED}${RESET}"

if [[ "${DRY_RUN}" == "false" && "${TOTAL_COPIED}" -gt 0 ]]; then
  echo ""
  info "Copied structure:"
  find "${PROMPTS_BASE}" -type d | sort | sed "s|${REPO_ROOT}/||"
fi

success "All done!"
