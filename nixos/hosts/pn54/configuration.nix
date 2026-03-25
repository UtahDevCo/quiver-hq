# nixos/hosts/pn54/configuration.nix
# NixOS host configuration for the ASUS PN54 (Ryzen 5) desktop – quiver-pn54.
{ config, pkgs, inputs, lib, ... }:

{
  imports = [
    # Shared settings: user accounts, zsh, tailscale, home-manager, etc.
    ../../common.nix

    # Hardware: AMD CPU/GPU, NVMe, UEFI boot.
    ./hardware-configuration.nix

    # Quiver HQ controller daemon (also runs on this host).
    ../../quiver-controller.nix

    # Desktop: Niri compositor, greetd, AMD graphics, Bluetooth, PipeWire.
    ../../../modules/nixos/desktop/niri.nix
  ];

  # ---------------------------------------------------------------------------
  # Host identity
  # ---------------------------------------------------------------------------
  networking.hostName = "quiver-pn54";
  networking.networkmanager.enable = true;
  users.users.chris.extraGroups = [ "networkmanager" "wheel" "video" ];
  hardware.enableRedistributableFirmware = true;
  boot.kernelPackages = pkgs.linuxPackages_xanmod_latest;
  boot.initrd.kernelModules = [ "mt7925e" ];
  networking.networkmanager.wifi.powersave = false;
  networking.networkmanager.unmanaged = [ "interface-name:lo" ];
  networking.networkmanager.settings = {
    device = {
      match-device = "mac:52:02:dc:4d:4a";
      managed = 1;
    };
  };
  networking.wireless.enable = lib.mkForce false;

  # Mountain Time – adjust if the machine moves.
  time.timeZone = lib.mkForce "America/Denver";

  # ---------------------------------------------------------------------------
  # Home Manager – override the user config to add desktop modules
  # ---------------------------------------------------------------------------
  # common.nix wires HM to nixos/home.nix (CLI-only).  Here we replace that
  # with pn54/home.nix which imports both the base config AND niri-config.nix.
  home-manager.users.chris = lib.mkForce (import ./home.nix);
  home-manager.extraSpecialArgs = { inherit inputs; };
  # ---------------------------------------------------------------------------
  # System state version
  # Keep in sync with common.nix; only bump intentionally.
  # ---------------------------------------------------------------------------
  system.stateVersion = lib.mkForce "24.11";

  console = {
    earlySetup = true;
    font = "ter-v16n";
    packages = [ pkgs.terminus_font ];
  };

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.grub.enable = false;

  # ---------------------------------------------------------------------------
  # 1Password GUI and CLI
  # ---------------------------------------------------------------------------
  programs._1password.enable = true;
  programs._1password-gui = {
    enable = true;
    polkitPolicyOwners = [ "chris" ];
  };
}
