# modules/home/desktop/niri-config.nix
# Home Manager module – configures the Niri compositor for a Samsung G9
# ultrawide, Apple Magic Trackpad input, Waybar, and the Foot terminal.
{ config, pkgs, lib, ... }:

{
  # ---------------------------------------------------------------------------
  # Niri compositor settings
  # ---------------------------------------------------------------------------
  # The niri HM module writes ~/.config/niri/config.kdl from these options.
  programs.niri.settings = {

    # -------------------------------------------------------------------------
    # Layout – optimised for a 49" Samsung G9 (5120×1440)
    # -------------------------------------------------------------------------
    layout = {
      # New windows open at 1/3 of the monitor width by default.
      # On the G9 (~5120 px) that is ~1707 px – a comfortable reading width.
      default-column-width = { proportion = 1.0 / 3.0; };

      gaps = 8;

      # Keep focused column stationary unless it is off-screen; avoids
      # jarring scrolls on an ultrawide where many columns are visible at once.
      center-focused-column = "never";

      struts = {
        top = 0;
        bottom = 0;
        left = 0;
        right = 0;
      };
    };

    # -------------------------------------------------------------------------
    # Input – Apple Magic Trackpad 2 (Bluetooth HID)
    # -------------------------------------------------------------------------
    input = {
      keyboard = {
        xkb = {
          layout = "us";
          # No special options needed for a standard US layout.
        };
      };

      # Niri applies these settings to any libinput touchpad device,
      # including the Magic Trackpad 2 once it is paired over Bluetooth.
      touchpad = {
        # Tap-to-click: one-finger = left, two-finger = right, three = middle.
        tap = true;
        # Natural (content-follows-finger) scrolling.
        natural-scroll = true;
        # clickfinger: number of fingers determines the click button, which
        # matches macOS behaviour and is recommended for the Magic Trackpad.
        click-method = "clickfinger";
        # Two-finger scrolling (the only sensible choice for the Magic Trackpad).
        scroll-method = "two-finger";
        # Disable touchpad while typing to prevent accidental cursor moves.
        dwt = true;
        # Increase accel speed slightly for the large Magic Trackpad surface.
        accel-speed = 0.2;
        accel-profile = "adaptive";
      };
    };

    # -------------------------------------------------------------------------
    # Workspaces – named tiers for a vertical-project workflow
    # Workspaces 2-6 are reserved for project contexts; 1 is general/admin.
    # -------------------------------------------------------------------------
    workspaces = [
      { name = "admin"; }     # workspace 1
      { name = "infra"; }     # workspace 2
      { name = "backend"; }   # workspace 3
      { name = "frontend"; }  # workspace 4
      { name = "ops"; }       # workspace 5
      { name = "lab"; }       # workspace 6
    ];

    # -------------------------------------------------------------------------
    # Key bindings
    # -------------------------------------------------------------------------
    # config.lib.niri.actions provides typed action constructors that are
    # validated by the niri Home Manager module at evaluation time.
    binds = with config.lib.niri.actions; {

      # --- Application launchers ---------------------------------------------
      # Mod+Enter  → open a Foot terminal
      "Mod+Return".action = spawn "foot";
      # Mod+Space  → fuzzel application launcher
      "Mod+Space".action = spawn "fuzzel";
      # Mod+Q      → close the focused window
      "Mod+Q".action = close-window;

      # --- Column-width presets (Samsung G9 ultrawide shortcuts) -------------
      # These keys are chosen to avoid collision with workspace move bindings.
      # Mod+Ctrl+1  → 1/3 width (default, ~1707 px on the G9)
      "Mod+Ctrl+1".action = set-column-width "33%";
      # Mod+Ctrl+2  → 1/2 width (~2560 px – side-by-side code+browser)
      "Mod+Ctrl+2".action = set-column-width "50%";
      # Mod+Ctrl+3  → full width (100% – immersive/reference mode)
      "Mod+Ctrl+3".action = set-column-width "100%";

      # --- Maximize toggle (mirrors the F11 habit from VS Code) --------------
      "Mod+F11".action = maximize-column;
      "Mod+Shift+F".action = maximize-column;

      # --- Focus navigation --------------------------------------------------
      "Mod+Left".action = focus-column-left;
      "Mod+Right".action = focus-column-right;
      "Mod+Up".action = focus-window-up;
      "Mod+Down".action = focus-window-down;
      "Mod+H".action = focus-column-left;
      "Mod+L".action = focus-column-right;
      "Mod+K".action = focus-window-up;
      "Mod+J".action = focus-window-down;

      # --- Column movement ---------------------------------------------------
      "Mod+Shift+Left".action = move-column-left;
      "Mod+Shift+Right".action = move-column-right;
      "Mod+Shift+H".action = move-column-left;
      "Mod+Shift+L".action = move-column-right;

      # --- Workspace focus (Mod+1 … Mod+6) ----------------------------------
      "Mod+1".action = focus-workspace 1;
      "Mod+2".action = focus-workspace 2;
      "Mod+3".action = focus-workspace 3;
      "Mod+4".action = focus-workspace 4;
      "Mod+5".action = focus-workspace 5;
      "Mod+6".action = focus-workspace 6;

      # --- Move active column to workspace (Mod+Shift+1 … Mod+Shift+6) -----
      "Mod+Shift+1".action = move-column-to-workspace 1;
      "Mod+Shift+2".action = move-column-to-workspace 2;
      "Mod+Shift+3".action = move-column-to-workspace 3;
      "Mod+Shift+4".action = move-column-to-workspace 4;
      "Mod+Shift+5".action = move-column-to-workspace 5;
      "Mod+Shift+6".action = move-column-to-workspace 6;

      # --- Session management -----------------------------------------------
      "Mod+Shift+E".action = quit;
      "Mod+Shift+R".action = reload-config;

      # --- Screenshot --------------------------------------------------------
      "Print".action = screenshot;
      "Mod+Shift+S".action = screenshot-screen;
    };
  };

  # ---------------------------------------------------------------------------
  # Waybar – status bar
  # ---------------------------------------------------------------------------
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
    polkit-gnome    # Authentication agent for privilege escalation dialogs
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
      ExecStart = "${pkgs.polkit-gnome}/libexec/polkit-gnome-authentication-agent-1";
      Restart = "on-failure";
    };
    Install.WantedBy = [ "graphical-session.target" ];
  };

  # Start the GNOME keyring daemon so apps can store/retrieve secrets.
  services.gnome-keyring = {
    enable = true;
    components = [ "pkcs11" "secrets" "ssh" ];
  };
}
