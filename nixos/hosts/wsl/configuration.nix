# /home/chris/dev/quiver-hq/nixos/hosts/wsl/configuration.nix
# This is the configuration specific to the WSL machine.
{ modulesPath, ... }:

{
  imports = [
    # Import the common configuration shared by all hosts
    ../../common.nix

    # Import the hardware configuration specific to this machine
    ./hardware-configuration.nix

    # Quiver HQ specific services
    ../../quiver-controller.nix
  ];

  # WSL-specific settings
  wsl.enable = true;
  wsl.defaultUser = "chris";

  # Disable the bootloader since WSL manages booting
  boot.loader.grub.enable = false;
  boot.loader.systemd-boot.enable = false;
  boot.loader.efi.canTouchEfiVariables = false;
  boot.isContainer = true;

  # The rest of your system's configuration comes from common.nix
}
