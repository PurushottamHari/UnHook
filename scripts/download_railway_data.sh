#!/usr/bin/env bash
# ============================================================
# download_railway_data.sh
#
# Downloads /app/data_collector_service and
# /app/data_processing_service from the corresponding Railway
# instances and saves them locally under:
#
#   downloads/railway/<timestamp>/data_collector_service/
#   downloads/railway/<timestamp>/data_processing_service/
#
# Prerequisites:
#   - Railway CLI installed and authenticated (`railway whoami`)
#   - SSH key registered with Railway (`railway ssh keys`)
#
# Usage:
#   ./scripts/download_railway_data.sh
#   ./scripts/download_railway_data.sh --dry-run
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
  warn "DRY RUN – no files will be downloaded or written"
fi

# --------------- sanity checks ------------------------------
step "Pre-flight checks"

if ! command -v railway &>/dev/null; then
  error "Railway CLI not found. Install it: https://docs.railway.app/guides/cli"
fi

if ! railway whoami &>/dev/null; then
  error "Not logged in to Railway. Run: railway login"
fi

# --------------- configuration ------------------------------
# Railway project names (as shown by `railway list`)
COLLECTOR_PROJECT="data_collector_service_worker"
PROCESSOR_PROJECT="data_processing_service_worker"

# The Railway service name that both projects use
RAILWAY_SERVICE="UnHook"

# Remote paths to download
COLLECTOR_REMOTE_PATH="/app/data_collector_service"
PROCESSOR_REMOTE_PATH="/app/data_processing_service"

# Local destination
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%dT%H%M%S)"
DOWNLOAD_BASE="${REPO_ROOT}/downloads/railway/${TIMESTAMP}"

# --------------- declare service configs -------------------
# Each entry: "<project_name>|<remote_path>|<local_dir_name>"
SERVICES=(
  "${COLLECTOR_PROJECT}|${COLLECTOR_REMOTE_PATH}|data_collector_service"
  "${PROCESSOR_PROJECT}|${PROCESSOR_REMOTE_PATH}|data_processing_service"
)

# --------------- main download loop -------------------------
step "Starting download run — ${TIMESTAMP}"
info "Destination: ${DOWNLOAD_BASE}"

TOTAL_SUCCESS=0
TOTAL_FAIL=0

for entry in "${SERVICES[@]}"; do
  IFS='|' read -r project remote_path local_dir <<< "${entry}"

  step "Service: ${project}"
  info "Remote path : ${remote_path}"
  local_dest="${DOWNLOAD_BASE}/${local_dir}"
  info "Local dest  : ${local_dest}"

  # ── 1. Link to the project/service ────────────────────────
  # --service hardcoded to avoid the interactive picker prompt
  info "Linking to Railway project '${project}' / service '${RAILWAY_SERVICE}'…"
  if [[ "${DRY_RUN}" == "false" ]]; then
    railway link \
      --project "${project}" \
      --service "${RAILWAY_SERVICE}" 2>&1 || error "Failed to link to project '${project}'"
  else
    info "[dry-run] would run: railway link --project '${project}' --service '${RAILWAY_SERVICE}'"
  fi
  success "Linked to '${project}' / service '${RAILWAY_SERVICE}'"

  # ── 2. Create local destination directory ────────────────
  if [[ "${DRY_RUN}" == "false" ]]; then
    mkdir -p "${local_dest}"
  else
    info "[dry-run] would mkdir -p '${local_dest}'"
  fi

  # ── 3. Stream tar archive over SSH → extract locally ─────
  #
  # `railway ssh -- <cmd>` runs <cmd> inside the container.
  # We pipe the tar stream through SSH to avoid needing scp/rsync.
  #
  # -C / strips the leading slash so extraction lands cleanly.
  info "Downloading '${remote_path}' via SSH tar…"
  REMOTE_TAR_CMD="tar czf - -C / ${remote_path#/}"

  if [[ "${DRY_RUN}" == "false" ]]; then
    # --project is intentionally omitted here: railway ssh reads the linked project
    # from ~/.railway/config.json (set by `railway link` above).
    # --service is passed explicitly to skip interactive prompts.
    if railway ssh --service "${RAILWAY_SERVICE}" -- ${REMOTE_TAR_CMD} \
        | tar xzf - -C "${local_dest}" --strip-components=1; then
      success "Downloaded '${project}' → ${local_dest}"
      TOTAL_SUCCESS=$(( TOTAL_SUCCESS + 1 ))
    else
      warn "Download failed for '${project}' (exit code $?)"
      TOTAL_FAIL=$(( TOTAL_FAIL + 1 ))
    fi
  else
    info "[dry-run] would run: railway ssh --service '${RAILWAY_SERVICE}' -- ${REMOTE_TAR_CMD}"
    info "[dry-run] piped to : tar xzf - -C '${local_dest}' --strip-components=1"
    TOTAL_SUCCESS=$(( TOTAL_SUCCESS + 1 ))
  fi
done

# --------------- summary ------------------------------------
step "Summary"
echo -e "  Timestamp  : ${BOLD}${TIMESTAMP}${RESET}"
echo -e "  Destination: ${BOLD}${DOWNLOAD_BASE}${RESET}"
echo -e "  ${GREEN}Succeeded${RESET}: ${TOTAL_SUCCESS}"
if [[ "${TOTAL_FAIL}" -gt 0 ]]; then
  echo -e "  ${RED}Failed${RESET}   : ${TOTAL_FAIL}"
fi

if [[ "${DRY_RUN}" == "false" && "${TOTAL_SUCCESS}" -gt 0 ]]; then
  echo ""
  info "Downloaded files:"
  find "${DOWNLOAD_BASE}" -type f | sort | sed "s|${REPO_ROOT}/||"
fi

if [[ "${TOTAL_FAIL}" -gt 0 ]]; then
  exit 1
fi

success "All done!"
