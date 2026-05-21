# modules/nixos/desktop/niri.nix
# System-level NixOS module for the Niri scrollable tiling compositor.
# Provides: Niri compositor, greetd login manager, AMD graphics, XDG portals,
#           PipeWire audio, and Bluetooth support for the Apple Magic Trackpad.
{ config, pkgs, lib, ... }:

{
  # ---------------------------------------------------------------------------
  # Compositor
  # ---------------------------------------------------------------------------
  # Installs niri, sets up PAM session, udev rules, and polkit support.
  programs.niri.enable = true;

  environment.sessionVariables = {
    NIXOS_OZONE_WL = "1";
    ELECTRON_OZONE_PLATFORM_HINT = "wayland";
  };

  # ---------------------------------------------------------------------------
  # Login manager – greetd + tuigreet (Wayland-native, minimal)
  # ---------------------------------------------------------------------------
  services.greetd = {
    enable = true;
    settings = {
      default_session = {
        # tuigreet remembers the last user and launches the Niri session.
        # Using niri-session (instead of raw niri) ensures that the systemd user manager
        # imports the Wayland environment and correctly brings up graphical-session.target.
        command = "${pkgs.tuigreet}/bin/tuigreet --time --remember --cmd 'niri-session'";
        user = "greeter";
      };
    };
  };

  # ---------------------------------------------------------------------------
  # XDG Desktop Portals (required by many Wayland apps)
  # ---------------------------------------------------------------------------
  xdg.portal = {
    enable = true;
    # Use gtk as the default backend, but GNOME specifically for screen sharing
    # and screenshots since Niri natively implements GNOME's Mutter screencast API.
    extraPortals = [
      pkgs.xdg-desktop-portal-gtk
      pkgs.xdg-desktop-portal-gnome
    ];
    config = {
      common = {
        default = "gtk";
      };
    };
  };

  # ---------------------------------------------------------------------------
  # AMD GPU – ASUS PN54 uses a Ryzen 5 with Radeon integrated graphics
  # ---------------------------------------------------------------------------
  services.xserver.videoDrivers = [ "amdgpu" ];

  hardware.graphics = {
    enable = true;
    # 32-bit support required for Steam, Wine, and similar applications.
    enable32Bit = true;
  };

  # ---------------------------------------------------------------------------
  # Audio – PipeWire (Wayland-preferred stack)
  # ---------------------------------------------------------------------------
  # Disable legacy PulseAudio in favour of PipeWire.
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;

  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    # PulseAudio compatibility layer so existing apps work without changes.
    pulse.enable = true;
  };

  # ---------------------------------------------------------------------------
  # Bluetooth – required for Apple Magic Trackpad 2
  # ---------------------------------------------------------------------------
  hardware.bluetooth = {
    enable = true;
    # Power on Bluetooth adapter at boot so the trackpad connects immediately.
    powerOnBoot = true;
    settings = {
      Policy = {
        # Re-enable adapter after reboot even if it was disabled in a prior session.
        AutoEnable = "true";
      };
      # Increase LE connection parameters for Apple peripherals:
      # tighter intervals reduce input latency for the Magic Trackpad.
      LE = {
        MinConnectionInterval = "6";
        MaxConnectionInterval = "9";
        ConnectionLatency = "0";
      };
    };
  };

  # Automatically connect to the Magic Trackpad on boot.
  systemd.services.connect-magic-trackpad = {
    description = "Connect Apple Magic Trackpad on boot";
    after = [ "bluetooth.service" ];
    requires = [ "bluetooth.service" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = pkgs.writeShellScript "connect-trackpad" ''
        MAC="10:94:BB:AA:C9:32"
        for i in {1..10}; do
          echo "Attempting to connect to Magic Trackpad ($MAC)..."
          ${pkgs.bluez}/bin/bluetoothctl connect $MAC && exit 0
          sleep 5
        done
        exit 1
      '';
      RemainAfterExit = true;
    };
  };

  # Blueman provides a system tray applet and GUI for pairing devices.
  services.blueman.enable = true;

  # hid-apple provides proper HID descriptors for Apple Bluetooth peripherals.
  boot.kernelModules = [ "hid-apple" ];

  # Magic Trackpad 2 needs the btusb driver with Apple quirks; these options
  # improve pointer precision and prevent firmware errors on the kernel side.
  boot.extraModprobeConfig = ''
    options hid_apple fnmode=1
  '';

  # ---------------------------------------------------------------------------
  # User groups for desktop hardware access
  # ---------------------------------------------------------------------------
  # These groups are additive – they merge with the groups set in common.nix.
  users.users.chris.extraGroups = [ "video" "audio" "input" ];

  # ---------------------------------------------------------------------------
  # System-level desktop packages
  # ---------------------------------------------------------------------------
  # Keep this list small: only truly system-wide tools that are not
  # user-configurable via Home Manager belong here.
  environment.systemPackages = with pkgs; [
    xwayland           # X11 compatibility layer for Wayland
    xdg-utils          # xdg-open, xdg-mime, etc.
    brightnessctl      # backlight control without root
    playerctl          # MPRIS media key control
    pamixer            # PulseAudio/PipeWire volume CLI tool
    libnotify          # notify-send for desktop notifications
  ];

  # ---------------------------------------------------------------------------
  # Network Manager (preferred over wpa_supplicant for desktop use)
  # ---------------------------------------------------------------------------
  networking.networkmanager.enable = true;
}
