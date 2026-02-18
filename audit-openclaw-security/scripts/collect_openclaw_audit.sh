#!/usr/bin/env bash
set -euo pipefail

# Collects defensive, mostly read-only diagnostics for an OpenClaw security audit.
# It does NOT run any --fix operations.
#
# Usage:
#   bash scripts/collect_openclaw_audit.sh --out ./openclaw-audit
#
# Notes:
# - Run on the OpenClaw host.
# - Output is stored in a folder with timestamped files.

OUT_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${OUT_DIR}" ]]; then
  echo "Missing --out <dir>" >&2
  exit 2
fi

TS="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT="${OUT_DIR%/}/openclaw-audit-${TS}"
mkdir -p "${ROOT}"

log() { echo "[collect] $*"; }

run_cmd() {
  local name="$1"; shift
  local file="${ROOT}/${name}.txt"
  log "Running: $*"
  {
    echo "$ $*"
    "$@"
  } > "${file}" 2>&1 || {
    echo "[warn] command failed (continuing): $*" >> "${file}"
    return 0
  }
}

# Basic host info
run_cmd "host_whoami" whoami
run_cmd "host_uname" uname -a

if command -v sw_vers >/dev/null 2>&1; then
  run_cmd "host_sw_vers" sw_vers
fi
if [[ -f /etc/os-release ]]; then
  run_cmd "host_os_release" cat /etc/os-release
fi

# OpenClaw info
if ! command -v openclaw >/dev/null 2>&1; then
  echo "openclaw not found on PATH" > "${ROOT}/openclaw_missing.txt"
  log "openclaw missing; collected host info only"
  exit 0
fi

run_cmd "openclaw_version" openclaw --version
run_cmd "openclaw_status_all" openclaw status --all
run_cmd "openclaw_doctor" openclaw doctor
run_cmd "openclaw_gateway_status" openclaw gateway status
run_cmd "openclaw_security_audit_json" openclaw security audit --json
run_cmd "openclaw_security_audit_deep_json" openclaw security audit --deep --json

# Network listeners (best-effort)
if command -v lsof >/dev/null 2>&1; then
  run_cmd "net_lsof_listen" lsof -nP -iTCP -sTCP:LISTEN
elif command -v ss >/dev/null 2>&1; then
  run_cmd "net_ss_listen" ss -ltnp
elif command -v netstat >/dev/null 2>&1; then
  run_cmd "net_netstat_listen" netstat -anv | head -n 2000
fi

# OpenClaw state dir perms (do not copy secrets; just record metadata)
STATE_DIR="${HOME}/.openclaw"
if [[ -d "${STATE_DIR}" ]]; then
  run_cmd "openclaw_state_ls" ls -la "${STATE_DIR}"
  if command -v stat >/dev/null 2>&1; then
    run_cmd "openclaw_state_stat" stat "${STATE_DIR}" "${STATE_DIR}/openclaw.json" 2>/dev/null || true
  fi
fi

log "Done. Output: ${ROOT}"
