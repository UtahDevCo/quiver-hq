# modules/home/desktop/niri-config.nix
# Home Manager module – configures the Niri compositor for a Samsung G9
# ultrawide, Apple Magic Trackpad input, Waybar, and the Foot terminal.
{ config, pkgs, lib, ... }:

{
  # ---------------------------------------------------------------------------
  # Session Variables – Wayland compatibility
  # ---------------------------------------------------------------------------
  home.sessionVariables = {
    # Forces Electron apps (Chrome, VS Code) to use Wayland natively.
    NIXOS_OZONE_WL = "1";
    ELECTRON_OZONE_PLATFORM_HINT = "wayland";
  };

  # ---------------------------------------------------------------------------
  # Niri compositor settings (Direct KDL)
  # ---------------------------------------------------------------------------
  xdg.configFile."niri/config.kdl".text = ''
    prefer-no-csd

    output "HDMI-A-1" {
        // Try values like 1.25, 1.5, or 2.0. 
        // 1.0 is the current default.
        scale 1.0
    }

    // Named workspaces
    workspace "admin"
    workspace "infra"
    workspace "backend"
    workspace "frontend"
    workspace "ops"
    workspace "lab"

    layout {
        gaps 0
        center-focused-column "never"
        default-column-width { proportion 0.33333; }
    }

    window-rule {
        geometry-corner-radius 0
        clip-to-geometry true
    }

    input {
        keyboard {
            xkb {
                layout "us"
            }
        }

        touchpad {
            tap
            natural-scroll
            click-method "clickfinger"
            scroll-method "two-finger"
            dwt
            accel-speed 0.2
            accel-profile "adaptive"
        }
    }

    spawn-at-startup "yambar"

    binds {
        // --- Application launchers ---
        // Mod is Super by default in niri unless bound otherwise
        Mod+Return { spawn "foot"; }
        Mod+Space { spawn "fuzzel"; }
        Mod+Q { close-window; }
        Mod+Tab { toggle-overview; }

        // --- Column-width presets ---
        Mod+Ctrl+1 { set-column-width "25%"; }
        Mod+Ctrl+2 { set-column-width "33.333%"; }
        Mod+Ctrl+3 { set-column-width "50%"; }
        Mod+Ctrl+4 { set-column-width "66.666%"; }
        Mod+Ctrl+5 { set-column-width "100%"; }
        Mod+R { switch-preset-column-width; }

        // --- Maximize toggle ---
        F11 { maximize-column; }
        Mod+F11 { maximize-column; }

        // --- Focus navigation ---
        Mod+Left  { focus-column-left; }
        Mod+Right { focus-column-right; }
        Mod+Up    { focus-window-up; }
        Mod+Down  { focus-window-down; }
        Mod+H     { focus-column-left; }
        Mod+L     { focus-column-right; }
        Mod+K     { focus-window-up; }
        Mod+J     { focus-window-down; }

        // --- Column/Window movement ---
        Mod+Shift+Left  { consume-or-expel-window-left; }
        Mod+Shift+Right { consume-or-expel-window-right; }
        Mod+Shift+Up    { move-window-up; }
        Mod+Shift+Down  { move-window-down; }
        Mod+Shift+H     { consume-or-expel-window-left; }
        Mod+Shift+L     { consume-or-expel-window-right; }
        Mod+Shift+K     { move-window-up; }
        Mod+Shift+J     { move-window-down; }

        // --- Entire Column movement ---
        Mod+Ctrl+Left  { move-column-left; }
        Mod+Ctrl+Right { move-column-right; }
        Mod+Ctrl+H     { move-column-left; }
        Mod+Ctrl+L     { move-column-right; }

        // --- Workspace navigation (Up/Down) ---
        Mod+Page_Down      { focus-workspace-down; }
        Mod+Page_Up        { focus-workspace-up; }
        Mod+Ctrl+Page_Down { move-column-to-workspace-down; }
        Mod+Ctrl+Page_Up   { move-column-to-workspace-up; }

        // --- Workspace focus ---
        Mod+1 { focus-workspace 1; }
        Mod+2 { focus-workspace 2; }
        Mod+3 { focus-workspace 3; }
        Mod+4 { focus-workspace 4; }
        Mod+5 { focus-workspace 5; }
        Mod+6 { focus-workspace 6; }

        // --- Move column to workspace ---
        Mod+Shift+1 { move-column-to-workspace 1; }
        Mod+Shift+2 { move-column-to-workspace 2; }
        Mod+Shift+3 { move-column-to-workspace 3; }
        Mod+Shift+4 { move-column-to-workspace 4; }
        Mod+Shift+5 { move-column-to-workspace 5; }
        Mod+Shift+6 { move-column-to-workspace 6; }

        // --- Session management ---
        Mod+Shift+E { quit; }

        // --- Shortcuts overlay ---
        Mod+Shift+Slash { show-hotkey-overlay; }

        // --- Screenshot ---
        Print { screenshot; }
        Mod+Shift+S { screenshot-screen; }

	Mod+T { spawn "alacritty"; }
	Mod+D { spawn "fuzzel"; }
    }
  '';

  # ---------------------------------------------------------------------------
  # Fuzzel – application launcher
  # ---------------------------------------------------------------------------
  programs.fuzzel = {
    enable = true;
    settings = {
      main = {
        font = "Noto Mono:size=11";
        terminal = "${pkgs.foot}/bin/foot";
        layer = "overlay";
      };
      colors = {
        background = "1e1e2ef2";
        text = "cdd6f4ff";
        match = "f38ba8ff";
        selection = "585b70ff";
        selection-text = "cdd6f4ff";
        border = "b4befeff";
      };
    };
  };

  # ---------------------------------------------------------------------------
  # Yambar – status bar
  # ---------------------------------------------------------------------------
  programs.yambar = {
    enable = true;
    settings = {
      bar = {
        location = "top";
        layer = "top";
        height = 30;
        background = "1a1b2bff";
        font = "Noto Sans:size=11";
        
        left = [];

        center = [
          {
            clock = {
              content = {
                string = { text = "{time}"; };
              };
            };
          }
        ];

        right = [];
      };
    };
  };
  programs.waybar.enable = false;

  # ---------------------------------------------------------------------------
  # Foot terminal
  # ---------------------------------------------------------------------------
  programs.foot = {
    enable = true;
    settings = {
      main = {
        font = "Noto Mono:size=11";
        # Pad the terminal slightly for readability on a high-DPI display.
        pad = "8x8";
      };

      scrollback = {
        lines = 10000;
      };

      colors = {
        # Catppuccin Mocha – matches the Waybar palette above.
        background = "1e1e2e";
        foreground = "cdd6f4";
        regular0   = "45475a";
        regular1   = "f38ba8";
        regular2   = "a6e3a1";
        regular3   = "f9e2af";
        regular4   = "89b4fa";
        regular5   = "f5c2e7";
        regular6   = "94e2d5";
        regular7   = "bac2de";
        bright0    = "585b70";
        bright1    = "f38ba8";
        bright2    = "a6e3a1";
        bright3    = "f9e2af";
        bright4    = "89b4fa";
        bright5    = "f5c2e7";
        bright6    = "94e2d5";
        bright7    = "a6adc8";
      };
    };
  };

  # ---------------------------------------------------------------------------
  # Additional user-level desktop packages
  # ---------------------------------------------------------------------------
  home.packages = with pkgs; [
    fuzzel          # Wayland-native application launcher (Mod+Space)
    pavucontrol     # PulseAudio/PipeWire volume control GUI
    grim            # Wayland screen-capture tool
    slurp           # Region selector for grim
    wl-clipboard    # wl-copy / wl-paste (Wayland clipboard CLI)
    gnome-keyring   # Secret storage (needed by many apps)
    polkit_gnome    # Authentication agent for privilege escalation dialogs

    alacritty
    firefox
  ];

  programs.chromium = {
    enable = true;
    package = pkgs.google-chrome;
    commandLineArgs = [
      "--ozone-platform=wayland"
      "--enable-features=UseOzonePlatform"
      "--force-device-scale-factor=1"
      "--disable-features=WaylandFractionalScaleV1"
      "--remote-debugging-port=9222"
      "--remote-debugging-address=0.0.0.0"
    ];
  };

  # Start the GNOME authentication agent on login so polkit prompts work.
  systemd.user.services.polkit-gnome-authentication-agent = {
    Unit = {
      Description = "GNOME Polkit authentication agent";
      After = [ "graphical-session.target" ];
      PartOf = [ "graphical-session.target" ];
    };
    Service = {
      Type = "simple";
      ExecStart = "${pkgs.polkit_gnome}/libexec/polkit-gnome-authentication-agent-1";
      Restart = "on-failure";
    };
    Install.WantedBy = [ "graphical-session.target" ];
  };

  # Start the GNOME keyring daemon so apps can store/retrieve secrets.
  services.gnome-keyring = {
    enable = true;
    components = [ "pkcs11" "secrets" "ssh" ];
  };

  programs.alacritty = {
    enable = true;
    
    settings = {
      font = {
        size = 9.0;
      };
      window.padding = {
        x = 10;
        y = 10;
      };
    };
  };

  gtk = {
    enable = true;
    font = {
      name = "Noto Sans";
      size = 11;
    };
    theme = {
      name = "Adwaita-dark";
      package = pkgs.gnome-themes-extra;
    };
  };

  qt = {
    enable = true;
    platformTheme.name = "gtk";
    style.name = "adwaita-dark";
  };
}
