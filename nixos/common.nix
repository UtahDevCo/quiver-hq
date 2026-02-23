# /home/chris/dev/quiver-hq/nixos/common.nix
# Common configuration shared across all hosts
{ inputs, pkgs, ... }:

{
  imports = [
    inputs.home-manager.nixosModules.default
  ];

  # Set your time zone.
  time.timeZone = "America/Los_Angeles";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  # Define a user account.
  users.users.chris = {
    isNormalUser = true;
    description = "Chris";
    extraGroups = [ "wheel" "networkmanager" ];
  };
  users.defaultUserShell = pkgs.zsh;

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # Enable flakes and the new nix command
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  # Enable Zsh system-wide
  programs.zsh.enable = true;

  # Enable nix-ld for running non-nix binaries
  programs.nix-ld.enable = true;

  # List packages installed in system profile.
  environment.systemPackages = with pkgs; [
    vim
    wget
    curl
    htop
    nix-ld
  ];

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
}
