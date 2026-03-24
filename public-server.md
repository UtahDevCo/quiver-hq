# Public Server: Self-Hosting Plan for Fizzy on NixOS

This document describes the architecture, implementation, and operational
guidance for self-hosting [Fizzy](https://github.com/basecamp/fizzy)
(`basecamp/fizzy`) on the `quiver-pn54` NixOS server using a private-first,
public-ready deployment model.

---

## Architecture Overview

```
Internet / Tailscale
        │
        ▼
   Caddy (TLS, gzip, asset caching)
   fizzy.chrisesplin.com → 127.0.0.1:8923
        │
        ▼
   Podman container (ghcr.io/basecamp/fizzy)
   localhost:8923 → container port 80
        │
        ├── SQLite databases  → /rails/storage/production*.sqlite3
        └── Uploaded files    → /rails/storage/production/files/
                (bind-mounted from /var/lib/fizzy/storage)
```

All components run on the same NixOS host.  Nothing is externalized.

---

## Why Caddy Instead of NGINX?

| Concern | NGINX + Certbot | Caddy |
|---|---|---|
| TLS certificate provisioning | Manual config + cron | Automatic (ACME built-in) |
| HTTP→HTTPS redirect | Extra `server {}` block | Implicit |
| Compression | Separate module config | Built-in gzip/zstd |
| Adding a new `*.chrisesplin.com` host | New config file + reload | One `virtualHosts` block in Nix |
| Memory footprint | ~5–10 MB + certbot process | ~15 MB all-in-one |
| NixOS module maturity | `services.nginx` (mature) | `services.caddy` (mature) |

For a single-operator always-on server where convenience and zero maintenance
overhead matter more than maximum raw throughput, Caddy's automatic TLS and
its single-service model are the better fit.  NGINX is a fine alternative if
you prefer it — the architecture is otherwise identical.

---

## How Tailscale and Caddy Complement Each Other

**Tailscale** is a zero-config VPN that makes the server reachable on a
private overlay network from any of your authenticated devices.  It requires
no port-forwarding, no DynDNS, and no inbound firewall rules.  Tailscale is
already enabled in `nixos/common.nix` for all hosts in this repo.

**Caddy** is the TLS-terminating reverse proxy that maps public (or
Tailscale-private) hostnames to backend services running on `localhost`.  It
handles certificate issuance and renewal, HTTP→HTTPS upgrading, compression,
and cache-header injection — all without touching the application container.

Together they give you two operating modes with almost zero configuration
change between them:

| Mode | How it works |
|---|---|
| **Phase 1 – Private (Tailscale)** | Firewall keeps ports 80/443 closed. You reach the service through your Tailscale overlay network. |
| **Phase 2 – Public** | Open ports 80/443, point DNS to the host's public IP, and Caddy auto-provisions a Let's Encrypt certificate. |

---

## Private-First Deployment Model

### Phase 1: Tailscale-Only Access

Deploy without opening any public ports.

1. Complete the [Initial Deployment Checklist](#initial-deployment-checklist).
2. Leave the firewall lines **commented out** in `nixos/fizzy.nix`:
   ```nix
   # networking.firewall.allowedTCPPorts = [ 80 443 ];
   ```
3. Access Fizzy from any of your Tailscale devices via the Caddy-managed
   hostname, or by pointing your local `/etc/hosts` (or Tailscale MagicDNS)
   at the server's Tailscale IP:
   ```
   100.x.y.z   fizzy.chrisesplin.com
   ```
   Alternatively, configure Caddy to bind on the Tailscale interface IP
   directly instead of all interfaces (advanced; not required for Phase 1).

### Phase 2: Evolving to Public Access

When you are ready to let collaborators access the service from the open web:

1. Set a public DNS `A` record for `fizzy.chrisesplin.com` pointing to the
   server's public IP address.
2. Uncomment the firewall rule in `nixos/fizzy.nix`:
   ```nix
   networking.firewall.allowedTCPPorts = [ 80 443 ];
   ```
3. Run `sudo nixos-rebuild switch`.
4. Caddy will automatically request and renew a Let's Encrypt certificate.
   No other changes are needed.

---

## Implementation Details

### Container: `ghcr.io/basecamp/fizzy`

Configuration lives in `nixos/fizzy.nix`.

#### Key findings from the Fizzy source code

| Finding | Impact on config |
|---|---|
| Working directory inside container is `/rails`, **not** `/app` | Volume must be `/var/lib/fizzy/storage:/rails/storage` |
| Production SQLite ships with **four databases** under `storage/` (primary, cable, cache, queue) | Mount the whole `storage/` directory; do not override `DATABASE_URL` for only the primary DB |
| Uploaded files land under `storage/production/files/` by default | Already covered by the full-directory mount |
| Container runs as **UID/GID 1000** (`rails` user) | Host directories must be owned by `1000:1000`, not `root` |
| Puma hard-codes `threads 1, 1` in production | `RAILS_MAX_THREADS` has no effect; omit it |
| `WEB_CONCURRENCY` controls Puma worker processes | Set to `1` on a shared machine |
| `JOB_CONCURRENCY` controls Solid Queue worker processes (defaults to CPU count) | Set to `1` to prevent queue workers from consuming excess RAM |
| Dockerfile `EXPOSE 80` (not 3000) | Map host port → container port 80 |

#### Port mapping

The Fizzy container exposes port **80** (not 3000).  To avoid conflicts with
other localhost services, the host binds a custom high port:

```
127.0.0.1:8923 → container:80
```

Caddy then proxies `fizzy.chrisesplin.com` → `127.0.0.1:8923`.

No service ever listens on port 3000 on the host.

#### Environment variables

| Variable | Value | Reason |
|---|---|---|
| `RAILS_ENV` | `production` | Required |
| `WEB_CONCURRENCY` | `1` | Single Puma worker; reduces RAM |
| `JOB_CONCURRENCY` | `1` | Single Solid Queue worker; reduces RAM |
| `BASE_URL` | `https://fizzy.chrisesplin.com` | Rails URL generation, redirects |
| `ACTIVE_STORAGE_SERVICE` | `local` | Use disk storage (OSS default) |
| `SECRET_KEY_BASE` | *(from env file)* | Do not hard-code — see below |

#### Persistence

```
/var/lib/fizzy/storage/        (host, owned 1000:1000)
  └── production.sqlite3
  └── production_cable.sqlite3
  └── production_cache.sqlite3
  └── production_queue.sqlite3
  └── production/
        └── files/             ← Active Storage uploads
```

The entire directory is bind-mounted into `/rails/storage` inside the
container.  This keeps all persisted state in one place and makes backups
trivial.

---

## Secret Handling

Secrets are **never** committed to the repository or stored in the Nix store.

The container receives them via an `environmentFiles` entry pointing to
`/run/secrets/fizzy.env`.  This file must be provisioned on the host before
running `nixos-rebuild switch`.

### Required secrets

```
# /run/secrets/fizzy.env
SECRET_KEY_BASE=<output of: openssl rand -hex 64>
```

### Provisioning

```bash
# Generate and write the file (root-only, not stored in Nix store)
echo "SECRET_KEY_BASE=$(openssl rand -hex 64)" | sudo tee /run/secrets/fizzy.env
sudo chmod 0400 /run/secrets/fizzy.env
sudo chown root:root /run/secrets/fizzy.env
```

> **Note:** `/run/secrets/` is a tmpfs mount and does not survive reboots.
> Use a secret manager (`sops-nix`, `agenix`, or a custom systemd unit that
> writes to `/run/secrets/` on boot) to re-provision the file automatically.
> The quiver-controller service in this repo uses `.env.secrets` as a model.

---

## Image Pinning

Do not use `latest` in production.  Find the current release tag:

```bash
# List available tags
curl -s https://ghcr.io/v2/basecamp/fizzy/tags/list \
  | python3 -m json.tool

# Or pull and check the digest
podman pull ghcr.io/basecamp/fizzy:1.0.0
podman inspect ghcr.io/basecamp/fizzy:1.0.0 --format '{{.Digest}}'
```

Then update `nixos/fizzy.nix`:

```nix
# Tag (easier to read):
image = "ghcr.io/basecamp/fizzy:1.0.0";

# Or digest (tamper-proof):
image = "ghcr.io/basecamp/fizzy@sha256:<hash>";
```

---

## Adding More `*.chrisesplin.com` Services

Caddy makes this trivial.  For each new service, add a new
`virtualHosts` block in or alongside `nixos/fizzy.nix`:

```nix
services.caddy.virtualHosts."another.chrisesplin.com" = {
  extraConfig = ''
    reverse_proxy 127.0.0.1:8924   # unique high port for each service
  '';
};
```

All services bind to `127.0.0.1` on unique custom ports; Caddy is the single
public-facing process on ports 80 and 443.

---

## Initial Deployment Checklist

```
[ ] 1. Pin the image
        Replace REPLACE_WITH_PINNED_TAG in nixos/fizzy.nix with a real tag.

[ ] 2. Provision the secret file
        echo "SECRET_KEY_BASE=$(openssl rand -hex 64)" \
          | sudo tee /run/secrets/fizzy.env
        sudo chmod 0400 /run/secrets/fizzy.env

[ ] 3. (Phase 1) Confirm firewall lines are commented out in nixos/fizzy.nix.

[ ] 4. Apply the configuration
        sudo nixos-rebuild switch

[ ] 5. Check container status
        systemctl status podman-fizzy.service
        journalctl -u podman-fizzy.service -f

[ ] 6. Validate the app boots
        curl -si http://127.0.0.1:8923/   # should return HTTP 200 or 302

[ ] 7. Verify SQLite databases are created on the host
        ls -lh /var/lib/fizzy/storage/

[ ] 8. Verify uploads persist (upload a file, restart container, confirm)
        sudo systemctl restart podman-fizzy.service

[ ] 9. Verify restart survives reboot
        sudo reboot
        systemctl is-active podman-fizzy.service   # should be "active"

[ ] 10. (Phase 2 only) Point DNS, uncomment firewall, rebuild, verify HTTPS
         curl -I https://fizzy.chrisesplin.com/
```

---

## Backup Guidance

All persistent state lives under `/var/lib/fizzy/storage/`.

### Recommended backup approach

```bash
#!/usr/bin/env bash
# /usr/local/bin/backup-fizzy.sh
set -euo pipefail

DEST="/var/backups/fizzy/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEST"

# SQLite hot backup (safe while the app is running)
for db in /var/lib/fizzy/storage/*.sqlite3; do
  sqlite3 "$db" ".backup '${DEST}/$(basename "$db")'"
done

# Uploaded files
if [ -d /var/lib/fizzy/storage/production/files ]; then
  cp -a /var/lib/fizzy/storage/production/files "$DEST/files"
fi

echo "Backup complete: $DEST"
```

Schedule with a NixOS systemd timer or cron.  Copy backups off-host to
object storage or another machine.

> **SQLite durability note:** SQLite is robust for single-writer workloads
> but susceptible to file-level corruption under abrupt power loss.  Enable
> WAL mode and back up regularly.  For higher durability requirements, migrate
> to the PostgreSQL configuration that Fizzy also supports.

---

## Security Notes

- The Fizzy container runs as non-root **UID/GID 1000** (`rails`).
- The container port is bound to **`127.0.0.1` only** — it is never directly
  reachable from the network.
- `SECRET_KEY_BASE` is injected from a root-owned `0400` file outside the
  Nix store.
- TLS is managed by Caddy (Let's Encrypt in Phase 2; self-signed or internal
  CA optional in Phase 1).
- Tailscale provides encrypted overlay networking for Phase 1 private access
  without opening any public ports.
- The `X-Forwarded-For` and `X-Real-IP` headers are set by Caddy so Rails
  can log real client IPs correctly.

---

## Caching Notes

Fizzy already ships production caching behaviour that works well behind Caddy:

- **Static assets** (`/assets/*`, `/packs/*`): fingerprinted by Rails and
  served with `Cache-Control: public, max-age=31536000, immutable` by the
  Caddy config in `nixos/fizzy.nix`.
- **Active Storage blobs**: Fizzy sets `expires_in 5.minutes, public: true`
  on disk controller responses — Caddy respects these headers automatically.
- **Gzip/zstd**: Caddy compresses all compressible responses by default,
  reducing bandwidth for HTML, JSON, and CSS.
