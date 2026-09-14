#!/usr/bin/env bash
# Local diagnostics only. Review captures before sharing: they are not redacted.
set -euo pipefail
umask 077
if [[ ${1:-} == -h || ${1:-} == --help ]]; then
  echo 'Usage: collect_openclaw_audit.sh --out DIR'
  exit 0
fi
if [[ $# != 2 || $1 != --out || -z $2 ]]; then
  echo 'Usage: collect_openclaw_audit.sh --out DIR' >&2
  exit 2
fi
mkdir -p "$2"
ROOT=$(mktemp -d "${2%/}/openclaw-audit-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")

run_cmd() {
  local name=$1 status=0
  shift
  { printf '$ %s\n' "$*"; "$@"; } > "$ROOT/$name.txt" 2>&1 || status=$?
  printf '%s\n' "$status" > "$ROOT/$name.exit-code"
  if [[ $status != 0 ]]; then
    printf '\n[warn] command exited %s; this check is incomplete\n' "$status" >> "$ROOT/$name.txt"
  fi
}

run_cmd host_whoami whoami
run_cmd host_uname uname -a
if command -v sw_vers >/dev/null; then
  run_cmd host_sw_vers sw_vers
  run_cmd macos_firewall_state /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
  run_cmd macos_firewall_stealth /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
  run_cmd macos_filevault fdesetup status
fi
if [[ -f /etc/os-release ]]; then run_cmd host_os_release cat /etc/os-release; fi
if command -v lsof >/dev/null; then
  run_cmd net_lsof_listen lsof -nP -iTCP -sTCP:LISTEN
elif command -v ss >/dev/null; then
  run_cmd net_ss_listen ss -ltnp
fi
for runtime in docker podman; do
  if command -v "$runtime" >/dev/null; then
    run_cmd "${runtime}_ps" "$runtime" ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
  fi
done

if command -v openclaw >/dev/null; then
  run_cmd openclaw_version openclaw --version
  run_cmd openclaw_status_all openclaw status --all
  run_cmd openclaw_status_deep openclaw status --deep
  run_cmd openclaw_gateway_status openclaw gateway status
  run_cmd openclaw_gateway_probe_json openclaw gateway probe --json
  run_cmd openclaw_channels_status_probe openclaw channels status --probe
  run_cmd openclaw_health_json openclaw health --json
  run_cmd openclaw_security_audit_json openclaw security audit --json
  run_cmd openclaw_security_audit_deep_json openclaw security audit --deep --json
  run_cmd openclaw_skills_eligible_json openclaw skills list --eligible --json
  run_cmd openclaw_plugins_list_json openclaw plugins list --json
  # No credential/config dumps, repair commands, implicit sudo, or backup creation.
  while IFS='|' read -r stem key; do
    run_cmd "openclaw_config_$stem" openclaw config get "$key"
  done <<'CONFIG'
gateway_bind|gateway.bind
gateway_auth_mode|gateway.auth.mode
gateway_auth_allow_tailscale|gateway.auth.allowTailscale
gateway_controlui_allowed_origins|gateway.controlUi.allowedOrigins
gateway_trusted_proxies|gateway.trustedProxies
gateway_allow_real_ip_fallback|gateway.allowRealIpFallback
discovery_mdns_mode|discovery.mdns.mode
session_dm_scope|session.dmScope
tools_profile|tools.profile
tools_fs_workspace_only|tools.fs.workspaceOnly
tools_exec_security|tools.exec.security
tools_elevated_enabled|tools.elevated.enabled
channels_defaults_dm_policy|channels.defaults.dmPolicy
channels_defaults_group_policy|channels.defaults.groupPolicy
logging_redact_sensitive|logging.redactSensitive
CONFIG
else
  printf '%s\n' 'OpenClaw unavailable; OpenClaw-specific checks were not run.' > "$ROOT/openclaw_missing.txt"
fi
STATE_DIR=${OPENCLAW_STATE_DIR:-$HOME/.openclaw}
if [[ -d $STATE_DIR ]]; then
  run_cmd openclaw_state_ls ls -ld "$STATE_DIR" "$STATE_DIR/openclaw.json"
fi
# Bash globbing works with macOS BSD utilities as well as GNU userlands.
for file in "$ROOT"/*; do printf '%s\n' "${file##*/}"; done | sort > "$ROOT/manifest.txt"
printf 'Captures: %s\nReview locally before sharing. Failed checks are not passes.\n' "$ROOT"
