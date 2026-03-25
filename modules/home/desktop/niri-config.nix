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
  };

  # ---------------------------------------------------------------------------
  # Chrome Flags – Force Wayland for Google Chrome
  # ---------------------------------------------------------------------------
  xdg.configFile."chrome-flags.conf".text = "--ozone-platform=wayland";
  xdg.configFile."google-chrome-flags.conf".text = "--ozone-platform=wayland";

  # ---------------------------------------------------------------------------
  # Niri compositor settings (Direct KDL)
  # ---------------------------------------------------------------------------
  xdg.configFile."niri/config.kdl".text = ''
    // Named workspaces
    workspace "admin"
    workspace "infra"
    workspace "backend"
    workspace "frontend"
    workspace "ops"
    workspace "lab"

    layout {
        gaps 8
        center-focused-column "never"
        default-column-width { proportion 0.33333; }
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

    spawn-at-startup "waybar"

    binds {
        // --- Application launchers ---
        // Mod is Super by default in niri unless bound otherwise
        Mod+Return { spawn "foot"; }
        Mod+Space { spawn "fuzzel"; }
        Mod+Q { close-window; }

        // --- Column-width presets ---
        Mod+Ctrl+1 { set-column-width "33%"; }
        Mod+Ctrl+2 { set-column-width "50%"; }
        Mod+Ctrl+3 { set-column-width "100%"; }

        // --- Maximize toggle ---
        Mod+F11 { maximize-column; }
        Mod+Shift+F { maximize-column; }

        // --- Focus navigation ---
        Mod+Left  { focus-column-left; }
        Mod+Right { focus-column-right; }
        Mod+Up    { focus-window-up; }
        Mod+Down  { focus-window-down; }
        Mod+H     { focus-column-left; }
        Mod+L     { focus-column-right; }
        Mod+K     { focus-window-up; }
        Mod+J     { focus-window-down; }

        // --- Column movement ---
        Mod+Shift+Left  { move-column-left; }
        Mod+Shift+Right { move-column-right; }
        Mod+Shift+H     { move-column-left; }
        Mod+Shift+L     { move-column-right; }

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

        // --- Screenshot ---
        Print { screenshot; }
        Mod+Shift+S { screenshot-screen; }

	Mod+T { spawn "alacritty"; }
	Mod+D { spawn "fuzzel"; }
    }
  '';

  # ---------------------------------------------------------------------------
  # Waybar – status bar
  # ---------------------------------------------------------------------------
  programs.fuzzel.enable = true;
  programs.waybar = {
    enable = true;

    settings = {
      mainBar = {
        layer = "top";
        position = "top";
        height = 30;

        modules-left = [
          "niri/workspaces"
          "niri/window"
        ];

        modules-center = [
          "clock"
        ];

        modules-right = [
          "pulseaudio"
          "network"
          "cpu"
          "memory"
          "bluetooth"
          "tray"
        ];

        "niri/workspaces" = {
          format = "{name}";
        };

        "niri/window" = {
          max-length = 60;
        };

        clock = {
          format = " {:%a %b %d  %H:%M}";
          tooltip-format = "<big>{:%Y %B}</big>\n<tt>{calendar}</tt>";
        };

        cpu = {
          format = " {usage}%";
          tooltip = false;
          interval = 5;
        };

        memory = {
          format = " {}%";
          interval = 10;
        };

        network = {
          format-wifi = " {essid} ({signalStrength}%)";
          format-ethernet = " {ifname}";
          format-disconnected = "⚠ Disconnected";
          tooltip-format = "{ifname}: {ipaddr}/{cidr}";
        };

        pulseaudio = {
          format = "{icon} {volume}%";
          format-muted = " muted";
          format-icons = {
            default = [ "" "" "" ];
          };
          on-click = "pavucontrol";
        };

        bluetooth = {
          format = " {status}";
          format-connected = " {device_alias}";
          tooltip-format = "{controller_alias}\t{controller_address}\n\n{num_connections} connected";
          tooltip-format-connected = "{controller_alias}\t{controller_address}\n\n{num_connections} connected\n\n{device_enumerate}";
          tooltip-format-enumerate-connected = "{device_alias}\t{device_address}";
          on-click = "blueman-manager";
        };

        tray = {
          spacing = 8;
        };
      };
    };

    style = ''
      * {
        font-family: "monospace";
        font-size: 13px;
        min-height: 0;
      }

      window#waybar {
        background-color: rgba(26, 27, 38, 0.92);
        color: #cdd6f4;
        border-bottom: 2px solid rgba(100, 114, 125, 0.5);
      }

      .modules-left,
      .modules-right,
      .modules-center {
        padding: 0 8px;
      }

      #workspaces button {
        padding: 0 8px;
        color: #6c7086;
        border-radius: 4px;
      }

      #workspaces button.active {
        color: #cdd6f4;
        background-color: rgba(100, 114, 125, 0.3);
      }

      #workspaces button:hover {
        color: #cba6f7;
      }

      #clock {
        color: #cba6f7;
        font-weight: bold;
      }

      #cpu    { color: #a6e3a1; }
      #memory { color: #89dceb; }

      #network {
        color: #89b4fa;
      }

      #pulseaudio {
        color: #f5c2e7;
      }

      #bluetooth {
        color: #74c7ec;
      }

      #tray {
        padding: 0 4px;
      }
    '';
  };

  # ---------------------------------------------------------------------------
  # Foot terminal
  # ---------------------------------------------------------------------------
  programs.foot = {
    enable = true;
    settings = {
      main = {
        font = "monospace:size=11";
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
    google-chrome
  ];

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
}
