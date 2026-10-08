# nixos/hosts/pn54/configuration.nix
# NixOS host configuration for the ASUS PN54 (Ryzen 5) desktop – quiver-pn54.
{ config, pkgs, inputs, lib, ... }:

{
  imports = [
    # Shared settings: user accounts, zsh, tailscale, home-manager, etc.
    ../../common.nix

    # Hardware: AMD CPU/GPU, NVMe, UEFI boot.
    ./hardware-configuration.nix

    # Desktop: Niri compositor, greetd, AMD graphics, Bluetooth, PipeWire.
    ../../../modules/nixos/desktop/niri.nix

    # Caddy reverse proxy for serving websites to Tailscale network.
    ../../caddy.nix
    ./fizzy.nix

  ];

  # ---------------------------------------------------------------------------
  # Host identity
  # ---------------------------------------------------------------------------
  networking.hostName = "quiver-pn54";
  networking.networkmanager.enable = true;
  systemd.services.NetworkManager.stopIfChanged = false;
  users.users.chris.extraGroups = [ "networkmanager" "wheel" "video" "onepassword-cli" "docker" ];
  hardware.enableRedistributableFirmware = true;
  boot.kernelPackages = pkgs.linuxPackages_xanmod_latest;
  boot.kernelParams = [ "ipv6.disable=1" ];
  boot.extraModprobeConfig = ''
    options mt7925e disable_ps=1
  '';
  boot.initrd.kernelModules = [ "mt7925e" ];
  networking.networkmanager.wifi.powersave = false;
  networking.networkmanager.unmanaged = [ "interface-name:lo" ];
  networking.networkmanager.settings = {
    main = {
      no-auto-default = "*";
    };
    keyfile = {
      unmanaged-devices = "none";
    };
    device = {
      "wifi.scan-rand-mac-address" = "no";
    };
    connection = {
      "ipv6.method" = "disabled";
    };
  };
  networking.networkmanager.wifi.backend = "iwd";
  networking.wireless.iwd.enable = true;
  networking.wireless.iwd.settings = {
    Settings = {
      AutoConnect = true;
    };
    General = {
      EnableNetworkConfiguration = true;
    };
    Network = {
      EnableIPv6 = false;
    };
  };
  networking.wireless.enable = false;
  services.openssh.enable = true;

  # ---------------------------------------------------------------------------
  # Tailscale (daemon enabled in common.nix)
  # ---------------------------------------------------------------------------
  # authKeyFile re-authenticates automatically after a logout or reboot, so the
  # node stays joined without a manual `tailscale up`. The file holds a reusable
  # auth key from the admin console (Settings → Keys); keep it out of git.
  # extraUpFlags must list every non-default pref or autoconnect's `up` errors.
  # useRoutingFeatures = "both" turns on IP forwarding, required to actually
  # serve as the advertised exit node.
  services.tailscale = {
    authKeyFile = "/var/lib/tailscale/authkey";
    useRoutingFeatures = "both";
    extraUpFlags = [ "--advertise-exit-node" "--operator=chris" ];
  };

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
  system.stateVersion = "24.11";

  console = {
    earlySetup = true;
    font = "ter-v20n";
    packages = [ pkgs.terminus_font ];
  };

  environment.systemPackages = (with pkgs; [
    wpa_supplicant
    iw
    iwd
    jq
  ]) ++ [
    # Latest upstream Signal Desktop (see flake.nix signalDesktopPackage).
    inputs.self.packages.${pkgs.stdenv.hostPlatform.system}.signal-desktop
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.grub.enable = false;

  # ---------------------------------------------------------------------------
  # Fingerprint Authentication
  # ---------------------------------------------------------------------------
  services.fprintd.enable = true;
  services.fprintd.tod.enable = true;
  services.fprintd.tod.driver = pkgs.libfprint-2-tod1-elan;
  security.pam.services.login.fprintAuth = true;
  security.pam.services.sudo.fprintAuth = true;

  # ---------------------------------------------------------------------------
  # 1Password GUI and CLI
  # ---------------------------------------------------------------------------
  programs._1password.enable = true;
  programs._1password-gui = {
    enable = true;
    polkitPolicyOwners = [ "chris" ];
  };

  # ---------------------------------------------------------------------------
  # Docker
  # ---------------------------------------------------------------------------
  virtualisation.docker.enable = true;
}
