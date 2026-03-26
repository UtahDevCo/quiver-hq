# /home/chris/dev/quiver-hq/nixos/home.nix
{ pkgs, lib, config, ... }:

{
  # Set your username and home directory
  home.username = "chris";
  home.homeDirectory = "/home/chris";

  home.file = {
    ".marks/dev".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev";
    ".marks/hq".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq";
    ".marks/j".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/job-harvester";
    ".marks/jh".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/job-harvester";
    ".marks/tah".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/therapyanimalhub.com";
    ".marks/tk".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/trikin";
    ".marks/v2".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/quiver-photos-v2";
    ".marks/v3".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/quiver-photos-v2";
    ".marks/w".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dev/quiver-hq/projects/wiley";
  };

  nixpkgs.config.allowUnfree = true;

  # Add any user-specific packages you want.
  home.packages = with pkgs; [
    git 
    direnv 
    nix-direnv 
    nodejs_24
    gh 
    github-copilot-cli
    google-cloud-sdk 
    gemini-cli
    fzf socat lsof
    zellij
    vscode
    xfce.thunar
    noto-fonts
    noto-fonts-color-emoji
  ];

  xdg.desktopEntries.vibetyper = {
    name = "VibeTyper";
    exec = "/home/chris/Downloads/VibeTyper.AppImage";
    icon = "vibe-typer";
    comment = "AI Voice Typing";
    categories = [ "Utility" ];
    terminal = false;
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
      export PATH="$HOME/bin:$HOME/.nix-profile/bin:$PATH"
      export PATH="$HOME/.npm-global/bin:$PATH"
      export NIX_LD_LIBRARY_PATH="/run/current-system/sw/share/nix-ld/lib"

      alias ll="ls -al"
      alias dc="docker compose"
      alias zshrc='vim ~/dev/quiver-hq/nixos/home.nix'
      alias reload='(cd ~/dev/quiver-hq && sudo nixos-rebuild switch --flake .#$(hostname))'
      alias opsignin='eval $(op signin)'
      alias qlogs='journalctl -u quiver-controller -f'
      alias qrestart='sudo systemctl restart quiver-controller'

      # 1. Setup Path
      export GOPATH=$HOME/go
      export PATH=$HOME/dev/quiver-hq/bin:$GOPATH/bin:$PATH

      # 2. Fetch API Keys with 1Password
      if [[ -z "$GEMINI_API_KEY" ]]; then
          export GEMINI_API_KEY=$(op read "op://Dev/quiver-hq/GEMINI_API_KEY" 2>/dev/null)
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

  programs.bash.enable = false;
  home.stateVersion = "23.11";
  programs.home-manager.enable = true;
}
