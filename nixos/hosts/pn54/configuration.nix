# nixos/hosts/pn54/configuration.nix
# NixOS host configuration for the ASUS PN54 (Ryzen 5) desktop – quiver-pn54.
{ lib, ... }:

{
  imports = [
    # Shared settings: user accounts, zsh, tailscale, home-manager, etc.
    ../../common.nix

    # Hardware: AMD CPU/GPU, NVMe, UEFI boot.
    ./hardware-configuration.nix

    # Quiver HQ controller daemon (also runs on this host).
    ../../quiver-controller.nix

    # Fizzy self-hosted bookmark manager (Podman + Caddy).
    ../../fizzy.nix

    # Desktop: Niri compositor, greetd, AMD graphics, Bluetooth, PipeWire.
    ../../../modules/nixos/desktop/niri.nix
  ];

  # ---------------------------------------------------------------------------
  # Host identity
  # ---------------------------------------------------------------------------
  networking.hostName = "quiver-pn54";

  # Mountain Time – adjust if the machine moves.
  time.timeZone = lib.mkForce "America/Denver";

  # ---------------------------------------------------------------------------
  # Home Manager – override the user config to add desktop modules
  # ---------------------------------------------------------------------------
  # common.nix wires HM to nixos/home.nix (CLI-only).  Here we replace that
  # with pn54/home.nix which imports both the base config AND niri-config.nix.
  home-manager.users.chris = lib.mkForce (import ./home.nix);

  # ---------------------------------------------------------------------------
  # System state version
  # Keep in sync with common.nix; only bump intentionally.
  # ---------------------------------------------------------------------------
  system.stateVersion = lib.mkForce "24.11";
}
