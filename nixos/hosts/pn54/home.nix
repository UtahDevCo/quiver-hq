# nixos/hosts/pn54/home.nix
# Home Manager configuration for the ASUS PN54 desktop.
# Extends the shared nixos/home.nix with the Niri desktop module.
{ pkgs, inputs, ... }:

{
  imports = [
    # Shared base: git, zsh, common CLI tools, etc.
    ../../home.nix

    # Niri compositor, Waybar, Foot terminal, and trackpad settings.
    ../../../modules/home/desktop/niri-config.nix
  ];
}
