# nixos/hosts/mac/configuration.nix
# This is the configuration specific to the macOS host (quiver-mac).
{ inputs, pkgs, ... }:

{
  imports = [
    inputs.home-manager.darwinModules.home-manager
  ];

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # Disable nix-darwin management of Nix to avoid conflicts with Determinate installer
  nix.enable = false;

  # Enable Zsh system-wide (nix-darwin will manage shell shells)
  programs.zsh.enable = true;

  # Define the user on macOS
  users.users.christopher = {
    name = "christopher";
    home = "/Users/christopher";
  };

  # Hook in Home Manager and tell it to use our home.nix
  home-manager = {
    useGlobalPkgs = true;
    useUserPackages = true;
    extraSpecialArgs = { inherit inputs; };
    backupFileExtension = "backup";
    users = {
      "christopher" = import ../../home.nix;
    };
  };

  # Used for backwards compatibility, please read the changelog before changing.
  # $ darwin-rebuild changelog
  system.stateVersion = 5;
}
