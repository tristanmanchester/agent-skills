---
name: audit-openclaw-security
description: Audit an OpenClaw deployment's gateway exposure, authentication, channel access, tool permissions, and secret handling. Use for OpenClaw security reviews or interpreting openclaw security audit results, not unrelated host hardening.
license: MIT
compatibility: OpenClaw CLI and a local shell for collection; Python 3.10+ for helpers. JSON5 redaction requires json5 or pyjson5.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Audit OpenClaw security

Audit systems the user owns or is authorised to assess. Start read-only; get approval for configuration changes, repairs, restarts, credential rotation, or exposure changes. Never request raw tokens, passwords, cookies, or credential stores.

## Establish the trust boundary

Record the installed OpenClaw version, host/container arrangement, gateway bind address, proxy/tunnel path, and who can send messages or invoke tools. One gateway is one trusted operator/team boundary, not isolation between mutually adversarial users. Use separate gateways and credentials for separate trust domains.

Host installs and container images can have different bind defaults. Inspect the running listener and published container ports rather than inferring exposure from the install method.

## Collect evidence

Resolve `SKILL_DIR` to the directory containing this file. Bundled paths are relative to that directory, not the project being audited. Keep output local and private until reviewed.

```bash
openclaw --version
openclaw security audit --help
openclaw security audit --json
openclaw security audit --deep --json
```

For a fuller host/network capture, run the bundled collector and renderer:

```bash
bash "$SKILL_DIR/scripts/collect_openclaw_audit.sh" --out ./openclaw-audit
python3 "$SKILL_DIR/scripts/render_report.py" --input ./openclaw-audit --output ./openclaw-security-report.md
```

Record failures and unsupported commands as missing evidence, never as passed checks. The renderer is a report aid, not a proof that the deployment is secure. CLI diagnostics can include private identifiers or sensitive free text; inspect them before sharing.

## Redact configuration only when necessary

Prefer targeted reads of non-secret settings over complete configuration exports. When a configuration must be shared:

```bash
python3 "$SKILL_DIR/scripts/redact_openclaw_config.py" ~/.openclaw/openclaw.json > openclaw.redacted.json
```

The helper parses JSON/JSON5, replaces complete values of sensitive fields, and removes credentials from URLs. It returns a non-zero status with empty stdout on invalid input. Install a JSON5 parser when required; do not fall back to regex editing of raw configuration. Comments disappear during parsing. Review unknown fields and free text manually: redaction is not an exhaustive secret detector. The output is not a restorable backup.

## Triage and remediate

1. Contain public exposure and open message surfaces with runtime/filesystem/elevated tools.
2. Verify gateway authentication, allowed origins, trusted proxies, and the real client-identity path. Tailscale Serve and public Funnel have different exposure; neither substitutes for checking access policy.
3. Review DM pairing/allowlists, group access, mention gates, and session isolation. A mention gate controls triggering, not a hostile-user security boundary.
4. Restrict tool, browser, node, plugin, and automation permissions to the task. Test the effective policy, not just its intended configuration.
5. Review credential, transcript, and log permissions and retention. Treat installed plugins and writable skills as executable supply-chain inputs.
6. For each approved change, capture the previous configuration securely, apply one coherent change, then rerun the relevant audit and functional checks. Preserve a rollback path.

Use the installed CLI and current official configuration schema for exact keys. Do not infer safety from an old check-ID list or blindly paste a platform baseline.

## Load supporting material when needed

- `references/platform-mac-mini.md`, `references/platform-personal-laptop.md`, `references/platform-docker.md`, or `references/platform-aws-ec2.md`: platform investigation prompts.
- `references/openclaw-audit-checks.md` and `assets/openclaw_checkid_map.json`: explanations for known findings; an unknown current check still needs triage.
- `assets/report-template.md`: final report structure.

Report scope/version, observed findings with redacted evidence, severity and impact, approved changes, verification results, and untested boundaries. Separate observations from proposals.

## Sources and validation

Reviewed 2026-09-13 against [OpenClaw security](https://docs.openclaw.ai/gateway/security), including its current trust-model, audit, network-exposure, and secrets sections. Consult those pages before changing security policy.

Run the offline redaction regressions with:

```bash
python3 -m unittest discover -s "$SKILL_DIR/tests" -v
```
