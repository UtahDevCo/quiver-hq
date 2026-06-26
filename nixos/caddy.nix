# nixos/caddy.nix
# Caddy reverse proxy service configuration for Quiver HQ
# Serves websites/services to Tailscale network with automatic HTTPS

{ config, pkgs, lib, inputs, ... }:

{
  # Enable Caddy service
  services.caddy = {
    enable = true;

    # Build Caddy with the Cloudflare DNS plugin
    package = (pkgs.caddy.withPlugins {
      plugins = [ "github.com/caddy-dns/cloudflare@v0.2.4" ];
      hash = "sha256-hEHgAG0F0ozHRAPuxEqLyTATBrE+pajeXDiSNwniorg=";
    }).overrideAttrs (old: {
      nativeBuildInputs = [ pkgs.go_1_26 ] ++ (lib.filter (p: p.pname or "" != "go") (old.nativeBuildInputs or []));
    });

    # Path to Caddyfile - relative paths are expanded to /etc/caddy/
    # We'll copy the Caddyfile to /etc/caddy/Caddyfile via environment.etc
    configFile = "/etc/caddy/Caddyfile";

    # Caddy will run as the 'caddy' user and group
    # This allows it to listen on ports 80 and 443 (privileged ports)
    user = "caddy";
    group = "caddy";

    # Enable log output
    logFormat = "json";

    # Environment file for secrets (Cloudflare API Token)
    environmentFile = "/var/lib/caddy/cloudflare.env";
  };

  # Ensure the caddy user exists and can listen on privileged ports
  users.users.caddy = {
    isSystemUser = true;
    group = "caddy";
  };
  users.groups.caddy = { };

  # Copy the Caddyfile to the system
  # This allows us to version control it in the repo while deploying via Nix
  environment.etc."caddy/Caddyfile".text = builtins.readFile (inputs.self + /Caddyfile);

  # Create a systemd override to ensure Caddy restarts on config changes
  # and has necessary capabilities to bind to privileged ports
  systemd.services.caddy = {
    # Additional environment variables (optional)
    environment = {
      # Uncomment for debugging:
      # DEBUG = "1";
    };

    # Restart the service if the Caddyfile changes
    restartTriggers = [ (builtins.readFile (inputs.self + /Caddyfile)) ];

    # Ensure Caddy can bind to ports 80 and 443
    serviceConfig = {
      AmbientCapabilities = [ "CAP_NET_BIND_SERVICE" ];
      Restart = "on-failure";
    };
  };

  # Firewall rules - allow HTTP and HTTPS traffic
  networking.firewall.allowedTCPPorts = [ 80 443 ];

  # Log rotation for Caddy
  services.logrotate.settings.caddy = {
    files = "/var/log/caddy/*.log";
    frequency = "weekly";
    rotate = 12;
    compress = true;
    delaycompress = true;
    notifempty = true;
    create = "0644 caddy caddy";
  };
}
