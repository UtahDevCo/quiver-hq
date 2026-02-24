# /home/chris/dev/quiver-hq/nixos/home.nix
{ pkgs, lib, ... }:

{
  # Set your username and home directory
  home.username = "chris";
  home.homeDirectory = "/home/chris";

  nixpkgs.config.allowUnfree = true;

  # Add any user-specific packages you want.
  home.packages = with pkgs; [
    git 
    direnv 
    nix-direnv 
    nodejs_22 
    gh 
    google-cloud-sdk 
    gemini-cli
    _1password-cli
    fzf socat
    vscode
  ];

  # Configure Git declaratively
  programs.git = {
    enable = true;
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

      alias ll="ls -al"
      alias zshrc='vim ~/dev/quiver-hq/nixos/home.nix'
      alias opsignin='eval $(op signin)'
      alias qlogs='journalctl -u quiver-controller -f'
      alias qrestart='sudo systemctl restart quiver-controller'

      # 1. Setup Path
      export GOPATH=$HOME/go
      export PATH=$GOPATH/bin:$PATH

      # 2. Fetch API Keys with 1Password
      if [[ -z "$GEMINI_API_KEY" ]]; then
          export GEMINI_API_KEY=$(op read "op://Personal/quiver-hq/GEMINI_API_KEY" 2>/dev/null)
      fi

      # 3. Setup direnv
      eval "$(direnv hook zsh)"
    '';
  };

  programs.bash.enable = false;
  home.stateVersion = "23.11";
  programs.home-manager.enable = true;
}
