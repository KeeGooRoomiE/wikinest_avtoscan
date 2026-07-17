# ansible/ — spare tire for VM redeployment

Not the routine deploy path — see [DEPLOYMENT.md](../DEPLOYMENT.md) for that
("Обновление кода": `git pull` + `docker compose up -d --build` + restart
caddy). This is what to run if the current VM is lost and you need a fresh
Ubuntu box brought to the same state from scratch.

## First-time setup

```bash
ansible-galaxy collection install -r requirements.yml
cp inventory.example.ini inventory.ini        # real host, real NAT ssh port
cp group_vars/all.yml.example group_vars/all.yml
```

`inventory.ini` and `group_vars/all.yml` are gitignored — they're allowed to
hold the real IP/port, same as `VM_SETUP.md`.

## Run

```bash
ansible-playbook -i inventory.ini playbook.yml --ask-become-pass
```

Prompts for `SECRET_KEY` (leave blank to auto-generate) and `GIT_PUSH_TOKEN`
(leave blank to skip — daily backup push stays off until you add it to
`.env` on the box and restart the backend). Neither is written anywhere
except the target VM's `.env`.

## What it does

Network/DNS defaults, UFW (SSH + 443 only — see Caddyfile for why not 80),
SSH hardening (no root login, key-only), the TCPMSS clamp that fixes a
Docker PMTUD blackhole we hit in July 2026 (containers could TCP-connect to
GitHub but the TLS handshake would hang — host-direct traffic was fine, only
container-NAT'd traffic broke), Docker Engine + Compose plugin, clone the
repo to `/srv/wikinest`, write `.env`, `docker compose up -d --build`.

## What it deliberately doesn't do

- Touch DNS/domain (`base.avtoscan42.ru` → new IP) — do that by hand after,
  per DEPLOYMENT.md "Домен".
- Re-run destructively — cloning never force-overwrites local commits, and
  `.env` is never rewritten once it exists.
