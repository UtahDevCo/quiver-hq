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
      EnvironmentFile = "/home/chris/dev/quiver-hq/.env.secrets";
      ExecStart = "/home/chris/dev/quiver-hq/bin/controller";
      Restart = "always";
      RestartSec = "10";
    };

    path = with pkgs; [
      go
      sqlite
      nix-ld
      git
      bash
      coreutils
      zsh
    ];
  };
}
