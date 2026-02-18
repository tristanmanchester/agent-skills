---
name: audit-openclaw-security
description: Audit and harden OpenClaw (Gateway + agents) security. Use when the user asks to "audit OpenClaw security", "secure/harden OpenClaw", troubleshoot risky exposure (e.g., port 18789), review OpenClaw gateway auth/tokens, DM/group policies, tool permissions (exec/fs), plugins/skills, secrets/log retention, or when deploying OpenClaw on a Mac mini, personal laptop, or cloud host (AWS EC2/VPS).
license: MIT
compatibility: Works best in Claude Code (local shell access). In Claude.ai, instruct the user to run the included scripts/commands locally and share redacted outputs (prefer `openclaw status --all` and `openclaw security audit --json`).
metadata:
  author: "community"
  version: "1.0.0"
  upstream: "OpenClaw docs + security guidance (Feb 2026)"
---

# audit-openclaw-security

Teach the agent to perform a **defensive, permissioned** security audit of an OpenClaw deployment and produce an actionable report + remediation plan.

OpenClaw is a *local-first* personal AI assistant with a Gateway control plane, multi-channel inbox, tools, and optional remote access patterns. The goal of this skill is to **reduce attack surface** (network + identity), **minimise agent permissions**, and **protect secrets/transcripts**.

## Scope and safety rules (non-negotiable)

1. **Only audit systems you own or have explicit permission to test.**
2. **Do not request or handle raw secrets.** Never ask for:
   - gateway tokens/passwords
   - model API keys / OAuth tokens
   - WhatsApp creds, Slack tokens, Discord tokens, etc.
3. Prefer outputs that are designed to be shareable/redacted:
   - `openclaw status --all` (shareable; redacts sensitive data)
   - `openclaw security audit --json`
4. Treat **any remote browser control / node pairing** as *admin-equivalent access* and audit accordingly.
5. If the user wants remediation, propose changes and get explicit approval before running any `--fix`, permission changes, restarts, or firewall edits.

## What “good” looks like (target posture)

- Gateway binds to loopback unless there is a strong reason otherwise.
- Strong Gateway auth (token/password) is enabled and rotated.
- No public internet exposure (no open security group / port-forward / reverse proxy).
- DMs require pairing or strict allowlists; group chats require explicit mention gating.
- Tooling is least-privilege (deny/ask for exec; workspace-only FS; no elevated tools unless required).
- Secrets are stored with tight filesystem permissions; logs/transcripts have a retention plan.
- Plugins/skills are explicitly trusted and minimal.

## Workflow

### Step 0 — Establish context (fast)

Collect just enough context to pick the right audit path:

- Where is OpenClaw running?
  - **Mac mini** (always-on home host)
  - **Personal laptop** (macOS/Windows/Linux)
  - **Cloud host** (AWS EC2 / VPS)
  - **Docker / container** vs “native” install
- Do we have **local shell access**?
  - **Claude Code**: can run commands directly
  - **Claude.ai**: user must run commands and paste outputs

Then pick one of the following modes:

- **Mode A: Assisted self-audit (Claude.ai)** — user runs commands/scripts, shares redacted output.
- **Mode B: Automated local audit (Claude Code)** — run scripts directly and generate a report.

---

## Mode A — Assisted self-audit (no local shell access)

Ask the user to run the following in a terminal **on the OpenClaw host** and paste results.

> If they are worried about sharing output, reassure them that `openclaw status --all` is designed to be shareable and redacts secrets. If they still refuse, fall back to high-level advice only.

#### 1) Collect OpenClaw posture

```bash
openclaw --version
openclaw status --all
openclaw doctor
openclaw gateway status
openclaw security audit --json
openclaw security audit --deep --json
```

If the user is comfortable, also request a **sanitised** config (never raw):

```bash
python3 scripts/redact_openclaw_config.py ~/.openclaw/openclaw.json > openclaw.json.redacted
```

#### 2) Collect host/network posture (pick the right block)

**macOS (Mac mini / Mac laptop):**
```bash
whoami
sw_vers
uname -a
# listening ports (focus on 18789)
lsof -nP -iTCP -sTCP:LISTEN
# macOS application firewall status
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
# basic disk encryption check
fdesetup status || true
```

**Linux (EC2/VPS):**
```bash
whoami
cat /etc/os-release
uname -a
ss -ltnp
sudo iptables -S || true
sudo nft list ruleset || true
sudo ufw status verbose || true
```

**Windows (recommended: WSL2 for OpenClaw):**
- Run OpenClaw commands inside WSL2.
- Provide `wsl --status` output if relevant.

---

## Mode B — Automated local audit (Claude Code)

If shell tools are available, run:

```bash
bash scripts/collect_openclaw_audit.sh --out ./openclaw-audit
python3 scripts/render_report.py --input ./openclaw-audit --output ./openclaw-security-report.md
```

Then open `openclaw-security-report.md`, refine wording, and present the report to the user.

---

## Analysis and reporting

### Step 1 — Triage findings by severity

Use the OpenClaw audit output as the source of truth and prioritise in this order:

1. **Public/network exposure + missing auth** (fix immediately)
2. **“Open” DMs or permissive group behaviour with tools enabled**
3. **Remote browser control / node pairing exposure**
4. **Filesystem permissions on `~/.openclaw` + config/credentials**
5. **Plugins/skills supply-chain risk**
6. **Model and prompt-injection resilience (secondary to access control)**

### Step 2 — Translate findings into a clear risk narrative

For each finding, capture:

- **What was observed** (quote the checkId/summary, but do not paste secrets)
- **Why it matters**
- **Impact** (data exfiltration, account takeover, unauthorised actions, supply-chain compromise)
- **Concrete remediation steps**
- **Verification** (how we know it’s fixed; usually rerun `openclaw security audit --deep`)

### Step 3 — Recommend a secure baseline configuration (when appropriate)

Offer the baseline below as a starting point and adapt based on the user’s needs (single-user vs shared inbox; required tools; remote access).

See: `references/openclaw-baseline-config.md`.

### Step 4 — Platform-specific guidance

Use the platform playbooks:

- `references/platform-mac-mini.md`
- `references/platform-personal-laptop.md`
- `references/platform-aws-ec2.md`

Do not assume cloud = secure. Cloud often increases risk due to public IPs, misconfigured security groups, and credential sprawl.

---

## Deliverable

Produce a **Markdown security audit report** using `assets/report-template.md`:

- Executive summary (1–2 paragraphs)
- Environment overview (host type, install type, exposure)
- Findings table (Critical/High/Medium/Low)
- Remediation plan (sequenced)
- Verification steps
- Residual risk + operational practices (patching, log retention, token rotation)

---

## Common remediation patterns (use with care)

### Network exposure
- Prefer Gateway bound to loopback and remote access via **SSH tunnel** or **Tailscale Serve**.
- Never expose the Gateway control UI directly to the public internet.
- If you must use a reverse proxy, ensure trusted proxy headers are correctly configured and direct access to the Gateway port is blocked.

### Identity & access
- Use token/password auth; rotate periodically and after any suspected leakage.
- Require DM pairing or strict allowlists.
- In groups, require explicit mention gating; avoid “always-on” bots in large groups.

### Least privilege tools
- Keep filesystem tools workspace-only.
- Keep exec denied or “ask always” unless the user is present and approving actions.
- Avoid enabling elevated tools unless absolutely necessary.

### Secrets and logs
- Tight permissions on `~/.openclaw` and `~/.openclaw/openclaw.json`.
- Treat session transcripts as sensitive.
- Set retention and redaction policies; avoid long-term storage of sensitive tool output.

---

## Troubleshooting

### “openclaw: command not found”
- Confirm OpenClaw CLI is installed and on PATH.
- If using Windows, prefer WSL2.
- Re-run installation via the official method for your platform; then re-run `openclaw --version`.

### “refusing to bind ... without auth”
- This is expected: non-loopback binds require auth configuration. Do not bypass this safety check.

### Audit output is empty or inconsistent
- Ensure the Gateway is running: `openclaw gateway status`
- Re-run with `--deep` for best-effort live probing.

---

## Trigger tests (for skill author)

Should trigger:
- “Can you audit my OpenClaw setup for security?”
- “My OpenClaw gateway is on port 18789 — is that safe?”
- “I deployed OpenClaw on EC2; give me a hardening checklist.”
- “Run openclaw security audit and interpret the results.”

Should NOT trigger:
- General macOS security advice unrelated to OpenClaw
- Generic AWS hardening unrelated to OpenClaw
- Unrelated software audits
