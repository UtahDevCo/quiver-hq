# /home/chris/dev/quiver-hq/nixos/home.nix
{ pkgs, lib, config, inputs, ... }:

let
  render-cli = pkgs.stdenv.mkDerivation {
    pname = "render-cli";
    version = "2.15.1";
    src = pkgs.fetchurl {
      url = "https://github.com/render-oss/cli/releases/download/v2.15.1/cli_2.15.1_linux_amd64.zip";
      sha256 = "1gq0djz31v41gvr1a3pwf3z022617ik83xl7h64md79vf80847df";
    };
    nativeBuildInputs = [ pkgs.unzip ];
    unpackPhase = "unzip $src";
    installPhase = ''
      mkdir -p $out/bin
      cp cli_v2.15.1 $out/bin/render
      chmod +x $out/bin/render
    '';
  };

  alpaca-cli = pkgs.buildGoModule {
    pname = "alpaca-cli";
    version = "0.0.11";
    src = pkgs.fetchFromGitHub {
      owner = "alpacahq";
      repo = "cli";
      rev = "v0.0.11";
      hash = "sha256-c49q7I+0H7SheMiVr/XBnxAD6X8gHLULn3RNyNKGQ+g=";
    };
    subPackages = [ "cmd/alpaca" ];
    vendorHash = "sha256-1jWJQwzS3PZlwX49hAJk8DGaIN2wUt6mzXilpSVKXFM=";
    meta = {
      description = "Alpaca Trading API CLI";
      mainProgram = "alpaca";
      homepage = "https://github.com/alpacahq/cli";
    };
  };

  # PWD-aware claude shim. aoe launches `claude` directly via tmux, bypassing
  # direnv/.envrc — so we route by working directory in the binary itself.
  # ~/.local/bin sits before /etc/profiles/... in PATH (see daemon env).
  claudeShim = pkgs.writeShellScript "claude" ''
    case "$PWD/" in
      "$HOME/dev/quiver-hq/projects/zamp/"*) \
        export CLAUDE_CONFIG_DIR="$HOME/.claude-zamp" ;;
      "$HOME/dev/quiver-hq/projects/zamp-worktrees/"*) \
        export CLAUDE_CONFIG_DIR="$HOME/.claude-zamp" ;;
      "$HOME/dev/quiver-hq/projects/foundation-web/"*) \
        export CLAUDE_CONFIG_DIR="$HOME/.claude-foundation" ;;
      "$HOME/dev/quiver-hq/projects/foundation-web-worktrees/"*) \
        export CLAUDE_CONFIG_DIR="$HOME/.claude-foundation" ;;
    esac
    exec ${pkgs.claude-code}/bin/claude "$@"
  '';
in
{
  # Set your username and home directory
  home.username = "chris";
  home.homeDirectory = "/home/chris";

  home.file = {
    ".local/bin/claude".source = claudeShim;
    ".marks/dev".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev";
    ".marks/hq".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq";
    ".marks/j".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/job-harvester";
    ".marks/jh".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/job-harvester";
    ".marks/tah".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/therapyanimalhub.com";
    ".marks/tk".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/trikin";
    ".marks/v2".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/quiver-photos-v2";
    ".marks/v3".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/quiver-photos-v2";
    ".marks/w".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/wiley";
    ".gemini".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/.agents";
      ".config/ghostty/config".text = ''
      theme = Catppuccin Mocha
      font-family = "JetBrainsMono Nerd Font"
      font-size = 12
      window-decoration = false
    '';
  };

  home.sessionVariables = {
    PUPPETEER_EXECUTABLE_PATH = "/etc/profiles/per-user/chris/bin/google-chrome";
    CHROME_PATH = "/etc/profiles/per-user/chris/bin/google-chrome";
  };

  nixpkgs.config.allowUnfree = true;

  # Add any user-specific packages you want.
  home.packages = with pkgs; [
    render-cli
    alpaca-cli
    inputs.self.packages.${pkgs.system}.quiver-secrets
    inputs.self.packages.${pkgs.system}.multica
    git 
    direnv 
    nix-direnv 
    nodejs_24
    gh 
    (github-copilot-cli.overrideAttrs (oldAttrs: {
      doInstallCheck = false;
    }))
    google-cloud-sdk 
    gemini-cli
    claude-code
    codex
    inputs.self.packages.${pkgs.system}.antigravity-cli
    inputs.self.packages.${pkgs.system}.antigravity-manager
    inputs.self.packages.${pkgs.system}.antigravity-ide
    dbeaver-bin
    fzf socat lsof
    ffmpeg
    appimage-run
    wl-clipboard
    zellij
    ghostty
    (warp-terminal.override { waylandSupport = true; })
    noto-fonts
    noto-fonts-color-emoji
    signal-desktop
  ];

  programs.yt-dlp = {
    enable = true;
    package = pkgs.yt-dlp.override { javascriptSupport = false; };
    settings = {
      js-runtimes = "node";
    };
  };

  programs.vscode = {
    enable = true;
    package = pkgs.vscode-fhs;
  };

  # Configure Zed editor
  programs.zed-editor = {
    enable = true;
    extensions = [ "nix" "toml" "rust" ];
    userSettings = {
      features = {
        copilot = true;
      };
      ui_font_family = "JetBrainsMono Nerd Font";
      buffer_font_family = "JetBrainsMono Nerd Font";
      theme = {
        mode = "system";
        dark = "One Dark";
        light = "One Light";
      };
    };
  };

  # Configure OpenCode AI Agent
  programs.opencode = {
    enable = true;
  };

  xdg.desktopEntries.beeper = {
    name = "Beeper";
    exec = "appimage-run /home/chris/dev/quiver-hq/assets/Beeper-4.2.670-x86_64.AppImage %u";
    icon = "/home/chris/dev/quiver-hq/assets/icon.png";
    comment = "Unified messenger";
    categories = [ "Network" "InstantMessaging" ];
    terminal = false;
    settings = {
      Type = "Application";
    };
  };

  xdg.desktopEntries.vibetyper = {
    name = "VibeTyper";
    exec = "env NO_DESKTOP_ENTRY=1 PASSWORD_STORE_BACKEND=gnome-libsecret appimage-run /home/chris/bin/VibeTyper.AppImage --password-store=gnome-libsecret %u";
    icon = "/home/chris/bin/vibe-typer.png";
    comment = "AI Voice Typing";
    categories = [ "Utility" "AudioVideo" ];
    terminal = false;
    mimeType = [ "x-scheme-handler/vibetyper" ];
    settings = {
      Type = "Application";
    };
  };

  # Configure Git declaratively
  programs.git = {
    enable = true;
    signing.format = "openpgp";
    settings = {
      user.name = "Chris Esplin";
      user.email = "chris@chrisesplin.com";
      init.defaultBranch = "master";
      core.editor = "vim";
      credential.helper = "cache";
      alias = {
        co = "checkout";
        br = "branch";
        ci = "commit";
        st = "status";
        lg = "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit";
        nuke = "!git branch | grep -v \"master\" | xargs git branch -D";
        upstream = "!git push -u origin HEAD";
        new = "co -b";
        remove = "br -D";
        "remove-remote" = "push origin --delete";
      };
    };
  };

  # Configure Zsh
  programs.zsh = {
    enable = true;

    oh-my-zsh = {
      enable = true;
      plugins = [ "git" "gh" "direnv" "gcloud" "jump" ];
      theme = "robbyrussell";
    };

    initContent = ''
      # 0. Ensure basic system tools are in PATH immediately
      export PATH="$HOME/.local/bin:$HOME/bin:$HOME/.nix-profile/bin:$PATH"
      # Prisma 7 on NixOS: point to nix-provided schema-engine so prisma generate
      # skips the CDN download (linux-nixos binaries are not always published).
      export PRISMA_SCHEMA_ENGINE_BINARY="${pkgs.prisma-engines}/bin/schema-engine"
      export PATH="$HOME/.npm-global/bin:$PATH"
      export NIX_LD_LIBRARY_PATH="/run/current-system/sw/share/nix-ld/lib"

      alias ll="ls -al"
      alias dc="docker compose"
      alias zshrc='vim ~/dev/quiver-hq/nixos/home.nix'
      alias reload='(cd ~/dev/quiver-hq && sudo nixos-rebuild switch --flake .#$(hostname))'
      alias agide='antigravity-ide'
      alias upgrade-agy='cd ~/dev/quiver-hq && bun /home/chris/.gemini/config/skills/antigravity-upgrade/scripts/upgrade.js --auto --rebuild && cd -'
      alias opsignin='eval $(op signin)'
      alias mlogs='journalctl --user -u multica-daemon -f'
      alias mrestart='systemctl --user restart multica-daemon'
      alias copilot='copilot'
      alias zed='zeditor'

      # 1. Setup Path
      export GOPATH=$HOME/go
      export PATH=$HOME/dev/quiver-hq/bin:$GOPATH/bin:$PATH
      export BUN_INSTALL="$HOME/.bun"
      export PATH="$BUN_INSTALL/bin:$PATH"

      # 2. Fetch API Keys with 1Password
      if [[ -z "$GEMINI_API_KEY" ]]; then
          export GEMINI_API_KEY=$(op read "op://Dev/quiver-hq/GEMINI_API_KEY" 2>/dev/null)
      fi
      if [[ -z "$ANTIGRAVITY_API_KEY" ]]; then
          export ANTIGRAVITY_API_KEY="$GEMINI_API_KEY"
      fi

      # 3.5. Setup Ghostty shell integration
      if [[ -n "$GHOSTTY_RESOURCES_DIR" ]]; then
          source "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration"
      fi

      # 3. Setup direnv
      eval "$(direnv hook zsh)"

      # 4. Auto-attach to zellij (optional, only if not already in a session)
      if [[ -z "$ZELLIJ" && $- == *i* ]]; then
          if zellij list-sessions 2>/dev/null | grep -q "EXITED"; then
              zellij delete-all-sessions --force
          fi
          # Uncomment the line below if you want to automatically start zellij
          # zellij attach -c default
      fi

      # 5. Fix jump plugin to resolve symlinks to physical paths
      # This prevents landing in the Nix store when jumping to a mark
      jump() {
          local mark=$1
          if [[ -z "$mark" ]]; then
              echo "Usage: jump <mark>"
              return 1
          fi
          if [[ -L "$HOME/.marks/$mark" ]]; then
              cd -P "$HOME/.marks/$mark"
          else
              cd "$HOME/.marks/$mark" 2>/dev/null || echo "No such mark: $mark"
          fi
      }

      # pk - Kill process(es) by port number
      # Usage: pk [port]
      #   With port: kills process on specified port
      #   Without port: kills processes on ports 3000-3030 and every 10th port from 3030-3120
      pk() {
          local port=$1

          # Function to kill a single port
          kill_port() {
              local p=$1
              local pids=$(lsof -ti :$p 2>/dev/null)

              # Fall back to ss if lsof doesn't work
              if [ -z "$pids" ]; then
                  pids=$(ss -tlnp 2>/dev/null | grep ":$p " | grep -oP 'pid=\K[0-9]+')
              fi

              if [ -n "$pids" ]; then
                  echo "Killing process(es) on port $p: $pids"
                  kill -9 $pids 2>/dev/null
                  if [ $? -eq 0 ]; then
                      echo "  ✓ Port $p freed"
                  else
                      echo "  ✗ Failed to kill process on port $p"
                  fi
              else
                  echo "No process found on port $p"
              fi
          }

          if [ -n "$port" ]; then
              # Kill specific port
              kill_port $port
          else
              # Kill ports 3000-3030
              echo "Killing ports 3000-3030..."
              for p in {3000..3030}; do
                  kill_port $p
              done

              echo ""
              echo "Killing every 10th port from 3030-3120..."
              # Kill every 10th port from 3030 to 3120
              for p in {3030..3120..10}; do
                  kill_port $p
              done

              echo ""
              echo "Done!"
          fi
      }
    '';
  };

  systemd.user.services.multica-daemon = lib.mkIf pkgs.stdenv.isLinux {
    Unit = {
      Description = "Multica local agent runtime";
      After = [ "network-online.target" ];
      Wants = [ "network-online.target" ];
    };
    Service = {
      Type = "simple";
      ExecCondition = "${pkgs.jq}/bin/jq -e '.token | strings | length > 0' %h/.multica/config.json";
      ExecStart = "${inputs.self.packages.${pkgs.system}.multica}/bin/multica daemon start --foreground --no-auto-update";
      Restart = "on-failure";
      RestartSec = 10;
      Environment = [
        "HOME=%h"
        "MULTICA_WORKSPACES_ROOT=%h/multica_workspaces"
        "PATH=%h/.nix-profile/bin:/etc/profiles/per-user/chris/bin:/run/current-system/sw/bin:%h/.local/bin:%h/.npm-global/bin:%h/.bun/bin:%h/go/bin"
      ];
    };
    Install.WantedBy = [ "default.target" ];
  };

  systemd.user.services.cli-pinger = lib.mkIf pkgs.stdenv.isLinux {
    Unit = {
      Description = "Ping Antigravity, Claude (foundation + zamp), and Codex CLIs to keep session quotas warm";
    };
    Service = {
      Type = "oneshot";
      WorkingDirectory = "/home/chris/dev/quiver-hq/projects/tools";
      ExecStart = "/home/chris/dev/quiver-hq/projects/tools/apps/cli-pinger/cli-ping.sh";
      Environment = [
        "HOME=%h"
        "PATH=/run/current-system/sw/bin:/etc/profiles/per-user/chris/bin:%h/.nix-profile/bin:%h/.npm-global/bin"
      ];
    };
  };

  systemd.user.timers.cli-pinger = lib.mkIf pkgs.stdenv.isLinux {
    Unit = {
      Description = "Trigger CLI pinger every ~5 hours";
    };
    Timer = {
      OnCalendar = [
        "*-*-* 00:00:00"
        "*-*-* 05:05:00"
        "*-*-* 10:10:00"
        "*-*-* 15:15:00"
        "*-*-* 20:20:00"
      ];
      Unit = "cli-pinger.service";
      Persistent = true;
    };
    Install = {
      WantedBy = [ "timers.target" ];
    };
  };

  programs.bash.enable = false;
  home.stateVersion = "24.11";
  programs.home-manager.enable = true;
}
