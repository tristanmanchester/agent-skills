# Domains and API keys

## Domain lifecycle

Use Domains whenever the task involves verified senders, DNS setup, regional routing, or inbound mail.

Stable domain endpoints:

- `POST /domains`
- `GET /domains`
- `GET /domains/{domain_id}`
- `PATCH /domains/{domain_id}`
- `DELETE /domains/{domain_id}`
- `POST /domains/{domain_id}/verify`

## Create-domain request options

The stable schema supports these important fields:

- `name` — required
- `region` — one of:
  - `us-east-1`
  - `eu-west-1`
  - `sa-east-1`
  - `ap-northeast-1`
- `custom_return_path` — advanced return-path subdomain
- `open_tracking` — boolean
- `click_tracking` — boolean
- `tls` — `opportunistic` or `enforced`
- `capabilities`:
  - `sending`: `enabled` or `disabled`
  - `receiving`: `enabled` or `disabled`

At least one domain capability should be enabled.

## DNS records

Domain objects return DNS records to configure. Stable record types include:

- **SPF**
- **DKIM**
- **Receiving**

Returned DNS record types may be:

- `TXT`
- `CNAME`
- `MX`

Record statuses typically move through:

- `not_started`
- `pending`
- `verified`
- `failed`
- `temporary_failure`

Recommended operational flow:

1. create the domain
2. apply the returned DNS records with your DNS provider
3. wait for propagation
4. call `/domains/{domain_id}/verify`
5. retrieve the domain until all records verify

## Receiving-capable domains

If the user wants inbound email on a custom domain:

- enable the domain's receiving capability
- configure the MX records returned by Resend
- if the root domain already has important MX records, prefer a dedicated subdomain such as
  `inbound.example.com` or `mail.example.com`

## Tracking and TLS updates

Use `PATCH /domains/{domain_id}` to update:

- `open_tracking`
- `click_tracking`
- `tls`
- `capabilities`

This is useful when the user wants to enable or disable tracking programmatically or switch TLS
mode after the initial setup.

## API keys

Stable key endpoints:

- `POST /api-keys`
- `GET /api-keys`
- `DELETE /api-keys/{api_key_id}`

Create-key request fields:

- `name` — required
- `permission` — `full_access` or `sending_access`
- `domain_id` — optional restriction when using `sending_access`

Important behaviour:

- the secret token is returned **when the key is created**
- store it immediately; do not assume it can be retrieved later from a list endpoint
- use `sending_access` plus `domain_id` for least-privilege sending agents where possible

## Practical guidance

### When to create a domain-scoped sending key

Use a domain-scoped `sending_access` key when:

- an agent only needs to send mail
- the sender must be constrained to one domain
- you want to reduce blast radius compared with a `full_access` key

### When to use `full_access`

Use `full_access` only if the workflow genuinely needs to manage domains, contacts, webhooks,
broadcasts, or other resources beyond sending.

## Minimal examples

### Create a domain

```bash
python3 scripts/resend_api.py request POST /domains --json-file assets/create-domain.json
```

### Create a least-privilege sending key

```bash
python3 scripts/resend_api.py request POST /api-keys --json-file assets/create-api-key.json
```

## Debug checklist

If domain setup is blocked:

1. inspect the returned DNS records
2. confirm the DNS provider copied names and values exactly
3. verify MX priority values where applicable
4. call the verify endpoint again after propagation
5. check whether sending vs receiving capability matches the intended use

## Useful assets

- `assets/create-domain.json`
- `assets/create-api-key.json`
