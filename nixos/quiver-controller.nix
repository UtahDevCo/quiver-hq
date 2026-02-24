# /home/chris/dev/quiver-hq/nixos/quiver-controller.nix
{ pkgs, ... }:

{
  systemd.services.quiver-controller = {
    description = "Quiver HQ Agentic Controller Daemon";
    after = [ "network.target" "tailscaled.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "chris";
      WorkingDirectory = "/home/chris/dev/quiver-hq";
      # We use a wrapper script to load 1Password secrets before starting
      ExecStart = "${pkgs.bash}/bin/bash -c 'source /home/chris/.zshrc; exec /home/chris/dev/quiver-hq/controller'";
      Restart = "always";
      RestartSec = "10";
    };

    path = with pkgs; [
      go
      sqlite
      _1password-cli
      git
      bash
      coreutils
    ];
  };
}
