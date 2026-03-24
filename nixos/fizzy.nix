# nixos/fizzy.nix
# Self-hosted Fizzy (basecamp/fizzy) bookmark manager.
#
# Architecture:
#   Podman container → localhost:8923 → Caddy → fizzy.chrisesplin.com
#
# Private-first deployment:
#   Phase 1 – Tailscale only.  Keep ports 80/443 closed in the firewall.
#             Access via your Tailscale node hostname (e.g.
#             https://quiver-pn54.<tailnet>.ts.net:8923 directly, or bind
#             Caddy to the Tailscale interface only).
#   Phase 2 – Public.  Point DNS for fizzy.chrisesplin.com to this machine,
#             open ports 80 and 443 in the firewall, and Caddy will
#             automatically provision a Let's Encrypt certificate.
#
# Secrets:
#   Create /run/secrets/fizzy.env before deploying (see public-server.md).
#   At minimum it must contain:
#     SECRET_KEY_BASE=<64-byte hex string>
#
# Image:
#   Replace REPLACE_WITH_PINNED_TAG with a concrete tag or digest, e.g.
#   ghcr.io/basecamp/fizzy:1.0.0  or  ghcr.io/basecamp/fizzy@sha256:<hash>
{ ... }:

{
  # ---------------------------------------------------------------------------
  # Container runtime
  # ---------------------------------------------------------------------------
  virtualisation.oci-containers.backend = "podman";

  # ---------------------------------------------------------------------------
  # Fizzy container
  # ---------------------------------------------------------------------------
  virtualisation.oci-containers.containers.fizzy = {
    # Pin to a concrete tag or digest before deploying.
    # Do NOT use "latest" in a long-running production deployment.
    image = "ghcr.io/basecamp/fizzy:REPLACE_WITH_PINNED_TAG";
    autoStart = true;

    # Bind to localhost on a custom high port (not 3000) to avoid conflicts.
    # The Fizzy Dockerfile EXPOSEs port 80 – map that to host port 8923.
    ports = [ "127.0.0.1:8923:80" ];

    environment = {
      RAILS_ENV = "production";

      # Memory tuning for a shared 32 GB machine.
      # - WEB_CONCURRENCY=1 → single Puma worker process (forks=1).
      # - JOB_CONCURRENCY=1 → single Solid Queue worker process.
      # Note: Fizzy's puma.rb hard-codes `threads 1, 1` in production, so
      # RAILS_MAX_THREADS has no effect and is intentionally omitted.
      WEB_CONCURRENCY = "1";
      JOB_CONCURRENCY = "1";

      # The public-facing URL used by Rails for URL generation and redirects.
      # During Phase 1 (Tailscale-only), you may set this to your Tailscale
      # node address; update it to the public domain in Phase 2.
      BASE_URL = "https://fizzy.chrisesplin.com";

      # Use Fizzy's built-in local disk Active Storage service (oss default).
      ACTIVE_STORAGE_SERVICE = "local";
    };

    # Secrets must NOT be hard-coded here.  Provision the file below before
    # running `nixos-rebuild switch`.  See public-server.md for details.
    #
    # Minimum required key:
    #   SECRET_KEY_BASE=<64-byte hex string>   # rails secret
    environmentFiles = [ "/run/secrets/fizzy.env" ];

    # Persist ALL of /rails/storage so every SQLite database and every
    # uploaded file survives container restarts and image upgrades.
    #
    # Fizzy's shipped config/database.sqlite.yml places four production
    # SQLite databases here (relative to Rails.root = /rails):
    #   storage/production.sqlite3
    #   storage/production_cable.sqlite3
    #   storage/production_cache.sqlite3
    #   storage/production_queue.sqlite3
    #
    # Uploaded files land under storage/production/files/ by default.
    # Mounting the whole directory is simpler and more complete than
    # overriding DATABASE_URL for only the primary database.
    volumes = [
      "/var/lib/fizzy/storage:/rails/storage"
    ];
  };

  # ---------------------------------------------------------------------------
  # Host directories – owned by UID/GID 1000 (the "rails" user inside the
  # container) so the app can write SQLite DBs and uploaded files.
  # ---------------------------------------------------------------------------
  systemd.tmpfiles.rules = [
    "d /var/lib/fizzy         0750 1000 1000 -"
    "d /var/lib/fizzy/storage 0750 1000 1000 -"
  ];

  # ---------------------------------------------------------------------------
  # Caddy reverse proxy
  # ---------------------------------------------------------------------------
  # Caddy is chosen over NGINX because:
  #   • Automatic HTTPS via Let's Encrypt with zero extra config.
  #   • Single declarative block handles TLS, HTTP→HTTPS redirect, and proxy.
  #   • Built-in gzip/zstd compression for Rails responses.
  #   • Lower runtime memory footprint than NGINX + certbot combination.
  #   • Easy to add future *.chrisesplin.com services as additional blocks.
  services.caddy = {
    enable = true;

    # Phase 2 (public): set DNS for fizzy.chrisesplin.com to this host's IP,
    # then open firewall ports 80 and 443 (see below).
    # Phase 1 (private): restrict access to your Tailscale interface by
    # binding Caddy to the Tailscale IP, e.g.
    #   virtualHosts."http://100.x.y.z:8923"
    virtualHosts."fizzy.chrisesplin.com" = {
      extraConfig = ''
        # Forward client IP to Rails (TRUSTED_PROXIES / ActionDispatch).
        header_up X-Forwarded-For {remote_host}
        header_up X-Real-IP {remote_host}

        # Long-lived caching for fingerprinted Rails assets.
        @assets path /assets/* /packs/*
        header @assets Cache-Control "public, max-age=31536000, immutable"

        reverse_proxy 127.0.0.1:8923
      '';
    };
  };

  # ---------------------------------------------------------------------------
  # Firewall
  # ---------------------------------------------------------------------------
  # Phase 1 (Tailscale-only): leave these commented out.  Access is then
  # possible only through your private Tailscale network.
  # Phase 2 (public): uncomment to allow Let's Encrypt ACME and web traffic.
  # networking.firewall.allowedTCPPorts = [ 80 443 ];
}
