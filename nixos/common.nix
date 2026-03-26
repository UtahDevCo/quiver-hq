# /home/chris/dev/quiver-hq/nixos/common.nix
# Common configuration shared across all hosts
{ inputs, pkgs, ... }:

{
  imports = [
    inputs.home-manager.nixosModules.default
  ];

  # Boot configuration
  boot.kernelModules = [ "uinput" ];

  # Set your time zone.
  time.timeZone = "America/Los_Angeles";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  # Define a user account.
  users.users.chris = {
    isNormalUser = true;
    description = "Chris";
    uid = 1001;
    extraGroups = [ "wheel" "networkmanager" ];
  };
  users.defaultUserShell = pkgs.zsh;

  security.sudo = {
    enable = true;
    wheelNeedsPassword = false;
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # Enable flakes and the new nix command
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
  nix.settings.sandbox = false;

  # Enable Zsh system-wide
  programs.zsh.enable = true;

  # Enable nix-ld for running non-nix binaries
  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [
      stdenv.cc.cc
      zlib
      fuse
      fuse3
      icu
      nss
      openssl
      curl
      expat
      glib
      libunwind
      libuuid
      krb5
      libsecret
      dbus
      p11-kit
      # Add more libraries as needed for VS Code extensions
    ];
  };

  # Enable gnome-keyring service
  services.gnome.gnome-keyring.enable = true;
  security.pam.services.chris.enableGnomeKeyring = true;

  # List packages installed in system profile.
  environment.systemPackages = with pkgs; [
    vim
    wget
    curl
    htop
    nix-ld
    tailscale
    gnome-keyring
    libsecret
  ];

  environment.variables = {
#    GOOGLE_CLOUD_PROJECT = "gen-lang-client-0493073390";
  };

  # Enable Tailscale service
  services.tailscale.enable = true;

  xdg.portal = {
    enable = true;
    extraPortals = [ pkgs.xdg-desktop-portal-gnome ];
    config.common.default = "*";
  };

  services.udev.extraRules = ''
    KERNEL=="uinput", MODE="0666", OPTIONS+="static_node=uinput"
    KERNEL=="event*", SUBSYSTEM=="input", MODE="0666"
  '';

  # Hook in Home Manager and tell it to use our home.nix
  home-manager = {
    extraSpecialArgs = { inherit inputs; };
    backupFileExtension = "backup";
    users = {
      "chris" = import ./home.nix;
    };
  };

  # Set the system state version
  system.stateVersion = "23.11";

  fonts = {
    fontDir.enable = true;
    packages = with pkgs; [
      nerd-fonts.jetbrains-mono
      nerd-fonts.symbols-only
    ];
  };
}
