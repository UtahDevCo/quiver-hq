# nixos/hosts/pn54/hardware-configuration.nix
# Template hardware configuration for the ASUS PN54 (Ryzen 5 series).
#
# IMPORTANT: Replace this file with the output of `nixos-generate-config`
# after booting the live NixOS installer on the actual machine:
#
#   nixos-generate-config --root /mnt
#
# The values below are representative for a PN54 with:
#   - AMD Ryzen 5 (Cezanne/Barcelo/Phoenix APU) with Radeon integrated graphics
#   - NVMe SSD (primary drive)
#   - UEFI firmware (Secure Boot disabled for NixOS compatibility)
#
# UUIDs and partition paths MUST be updated to match your actual disks.
{ config, lib, pkgs, modulesPath, ... }:

{
  imports = [
    (modulesPath + "/installer/scan/not-detected.nix")
  ];

  # AMD Ryzen 5 – required kernel modules
  boot.initrd.availableKernelModules = [
    "nvme"
    "xhci_pci"
    "ahci"
    "usbhid"
    "usb_storage"
    "sd_mod"
  ];
  boot.initrd.kernelModules = [ "amdgpu" ];
  boot.kernelModules = [ "kvm-amd" ];
  boot.extraModulePackages = [ ];

  # UEFI / systemd-boot loader
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # ---------------------------------------------------------------------------
  # File systems
  # REPLACE the UUIDs below with the output of `blkid` on the target machine.
  # ---------------------------------------------------------------------------

  # EFI system partition
  fileSystems."/boot" = {
    # device = "/dev/disk/by-uuid/REPLACE-WITH-EFI-UUID";
    device = "/dev/disk/by-label/EFI";
    fsType = "vfat";
    options = [ "fmask=0022" "dmask=0022" ];
  };

  # Root partition (ext4; swap for btrfs if preferred)
  fileSystems."/" = {
    # device = "/dev/disk/by-uuid/REPLACE-WITH-ROOT-UUID";
    device = "/dev/disk/by-label/nixos";
    fsType = "ext4";
  };

  # Swap partition – optional for a desktop with ample RAM.
  # Uncomment and update the UUID if you want a dedicated swap partition.
  # On modern systems with 16–32 GB RAM a swap file may be sufficient.
  swapDevices = [
    # { device = "/dev/disk/by-uuid/REPLACE-WITH-SWAP-UUID"; }
  ];

  # ---------------------------------------------------------------------------
  # Platform
  # ---------------------------------------------------------------------------
  networking.useDHCP = lib.mkDefault true;
  nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";

  # Power management – recommended for AMD laptops/mini-PCs
  powerManagement.cpuFreqGovernor = lib.mkDefault "schedutil";
}
