{
  description = "Quiver HQ Agentic Dev Environment & Multi-Host NixOS Config";

  inputs = {   
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nixos-wsl = {
      url = "github:nix-community/NixOS-WSL";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nix-darwin = {
      url = "github:lnl7/nix-darwin";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    agent-of-empires = {
      url = "github:agent-of-empires/agent-of-empires";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nixos-wsl, home-manager, nix-darwin, ... }@inputs:
    let
      # Define systems for which we want to build shells and packages
      supportedSystems = [ "x86_64-linux" "aarch64-darwin" ];

      # Helper function to generate package sets for each system
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Nixpkgs for each system
      pkgs = forAllSystems (system: import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      });
       # Helper to build all packages in cmd/
       allCmdPackages = system:
         let
           cmdDir = ./cmd;
           cmds = builtins.attrNames (builtins.readDir cmdDir);
           pkgs_ = pkgs.${system};
         in
         builtins.listToAttrs (map (name: {
           name = name;
           value = pkgs_.buildGoModule {
             pname = name;
             version = "0.1.0";
             src = ./.;
             subPackages = [ "cmd/${name}" ];
             vendorHash = "sha256-5uJYNIjm5mXndjl7/pW3lmCtYqG1j/zT0R4PBeHliZc=";
           };
         }) cmds);
      antigravityPackages = system:
        let
          pkgs_ = pkgs.${system};
        in
        if system == "x86_64-linux" then
          let
            antigravityIcon = pkgs_.fetchurl {
              url = "https://antigravity.google/assets/image/antigravity-logo.png";
              hash = "sha256-jwuV0tIdv5MLTRAOL9xFBWc+kApzGqVupjOktZwxJ5k=";
            };
             antigravityRuntimeLibs = with pkgs_; [
               alsa-lib
               atk
               cairo
               cups
              dbus
              expat
              fontconfig
              freetype
              libgbm
               glib
               gtk3
               libdrm
               libsecret
               libglvnd
               libxkbcommon
               mesa
               nspr
               nss
               pango
               stdenv.cc.cc
               systemd
               wayland
               libx11
               libxcomposite
               libxcursor
               libxdamage
               libxext
               libxfixes
               libxi
               libxinerama
               libxrandr
               libxrender
               libxscrnsaver
               libxtst
               libxcb
               libxkbfile
               libxshmfence
               zlib
             ];
             runtimeLibPath = pkgs_.lib.makeLibraryPath antigravityRuntimeLibs;
             mkAntigravityApp = {
               pname,
               version,
              src,
              sourceRoot,
              execPath,
              binName,
              desktopName,
              comment,
              categories ? [ "Development" ],
            }:
               pkgs_.stdenv.mkDerivation {
                 inherit pname version src sourceRoot;
                 buildInputs = [
                   pkgs_.gtk3
                   pkgs_.gsettings-desktop-schemas
                 ];
                 nativeBuildInputs = [
                   pkgs_.copyDesktopItems
                   pkgs_.glib
                   pkgs_.makeWrapper
                   pkgs_.wrapGAppsHook3
                   pkgs_.asar
                   pkgs_.nodejs
                 ];
                 dontConfigure = true;
                 dontBuild = true;
                 dontWrapGApps = true;
                 desktopItems = [
                  (pkgs_.makeDesktopItem {
                    name = pname;
                    inherit desktopName comment categories;
                    exec = binName;
                    icon = pname;
                    terminal = false;
                  })
                ];
                installPhase = ''
                  runHook preInstall

                   mkdir -p \
                     $out/bin \
                     $out/libexec/${pname} \
                     $out/share/glib-2.0/schemas \
                     $out/share/icons/hicolor/512x512/apps
                   cp -R . $out/libexec/${pname}
                   chmod -R u+w $out/libexec/${pname}

                    if [ -f $out/libexec/${pname}/resources/app.asar ]; then
                      echo "Patching app.asar for ${pname}..."
                      tmp_asar_dir="$(mktemp -d)"
                      asar extract $out/libexec/${pname}/resources/app.asar "$tmp_asar_dir"

                      # Patch second-instance handler to open a new window if wins.length is 0
                      node -e '
                        const fs = require("fs");
                        let content = fs.readFileSync(process.argv[1] + "/dist/main.js", "utf8");
                        const target = "if (wins.length > 0) {\n        if (wins[0].isMinimized()) {\n            wins[0].restore();\n        }\n        wins[0].show();\n        wins[0].focus();\n        electron_1.app.focus({ steal: true });\n    }";
                        const replacement = "if (wins.length > 0) {\n        if (wins[0].isMinimized()) {\n            wins[0].restore();\n        }\n        wins[0].show();\n        wins[0].focus();\n        electron_1.app.focus({ steal: true });\n    } else if (!HEADLESS) {\n        const url = constants_1.WINDOW_ORIGIN + \":\" + (0, languageServer_1.getLsPort)() + \"/\";\n        (0, utils_1.createWindow)(url);\n    }";
                        if (!content.includes(target)) {
                            console.error("Target not found in main.js!");
                            process.exit(1);
                        }
                        content = content.replace(target, replacement);
                        fs.writeFileSync(process.argv[1] + "/dist/main.js", content, "utf8");
                      ' "$tmp_asar_dir"

                      # Patch default RUN_IN_BACKGROUND to false on Linux/Windows
                      node -e '
                        const fs = require("fs");
                        let content = fs.readFileSync(process.argv[1] + "/dist/services/settingsService.js", "utf8");
                        const target = "process.platform !== \x27win32\x27";
                        const replacement = "process.platform === \x27darwin\x27";
                        if (!content.includes(target)) {
                            console.error("Target not found in settingsService.js!");
                            process.exit(1);
                        }
                        content = content.replace(target, replacement);
                        fs.writeFileSync(process.argv[1] + "/dist/services/settingsService.js", content, "utf8");
                      ' "$tmp_asar_dir"

                      asar pack "$tmp_asar_dir" $out/libexec/${pname}/resources/app.asar
                      rm -rf "$tmp_asar_dir"
                    fi

                   schemaDir="$(mktemp -d)"
                   cp ${pkgs_.gtk3}/share/gsettings-schemas/${pkgs_.gtk3.name}/glib-2.0/schemas/*.xml "$schemaDir"/
                   cp ${pkgs_.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs_.gsettings-desktop-schemas.name}/glib-2.0/schemas/*.xml "$schemaDir"/
                   glib-compile-schemas "$schemaDir"
                   cp "$schemaDir"/* $out/share/glib-2.0/schemas/
                   install -Dm644 ${antigravityIcon} $out/share/icons/hicolor/512x512/apps/${pname}.png

                    makeWrapper $out/libexec/${pname}/${execPath} $out/bin/${binName} \
                      --set LD_LIBRARY_PATH "${runtimeLibPath}" \
                      --set GSETTINGS_SCHEMA_DIR "$out/share/gsettings-schemas/${pname}-${version}/glib-2.0/schemas" \
                      "''${gappsWrapperArgs[@]}"

                   runHook postInstall
                 '';
                meta = {
                  description = comment;
                  mainProgram = binName;
                  platforms = [ "x86_64-linux" ];
                 };
               };
             mkAntigravityCli = {
               version,
               url,
               hash,
             }:
               pkgs_.stdenvNoCC.mkDerivation {
                 pname = "antigravity-cli";
                 inherit version;
                 src = pkgs_.fetchurl {
                   inherit url hash;
                 };
                 nativeBuildInputs = [ pkgs_.gnutar ];
                 dontConfigure = true;
                 dontBuild = true;
                 unpackPhase = ''
                   runHook preUnpack
                   tar -xzf $src
                   runHook postUnpack
                 '';
                 installPhase = ''
                   runHook preInstall
                   mkdir -p $out/bin
                   install -Dm755 antigravity $out/bin/agy
                   ln -s agy $out/bin/antigravity-cli
                   runHook postInstall
                 '';
                 meta = {
                   description = "Google Antigravity CLI";
                   mainProgram = "agy";
                   platforms = [ "x86_64-linux" ];
                 };
               };
           in
           {
             antigravity-cli = mkAntigravityCli {
               version = "1.0.4-6513644876464128";
               url = "https://storage.googleapis.com/antigravity-public/antigravity-cli/1.0.4-6513644876464128/linux-x64/cli_linux_x64.tar.gz";
               hash = "sha256-Nz9ULRd9M7k76FfQfTWladctMwzgqLSTF8uKPtaBTuI=";
             };
             antigravity-manager = mkAntigravityApp {
               pname = "antigravity-manager";
               version = "100.0.0-6081531354152960";
               src = pkgs_.fetchurl {
                url = "https://storage.googleapis.com/antigravity-public/antigravity-hub/100.0.0-6081531354152960/linux-x64/Antigravity.tar.gz";
                hash = "sha256-UDWduWkpG9VK9jVZygjK8f/jWreDQBrUzpPjnDdO0Ug=";
              };
              sourceRoot = "Antigravity-x64";
              execPath = "antigravity";
              binName = "antigravity";
              desktopName = "Antigravity";
              comment = "Google Antigravity manager";
            };
            antigravity-ide = mkAntigravityApp {
              pname = "antigravity-ide";
              version = "2.0.1-4861014005645312";
              src = pkgs_.fetchurl {
                url = "https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.0.1-4861014005645312/linux-x64/Antigravity%20IDE.tar.gz";
                hash = "sha256-dHFjqjqK+6SzFvl8QLSnXKRzall2ikFs0eiB5z7DHvk=";
              };
              sourceRoot = "Antigravity IDE";
              execPath = "bin/antigravity-ide";
              binName = "antigravity-ide";
              desktopName = "Antigravity IDE";
              comment = "Google Antigravity IDE";
               categories = [ "Development" "IDE" ];
            };
          }
        else
          { };

      investingScreenerPackage = system:
        let
          pkgs_ = pkgs.${system};
        in
        {
          investing-screener = pkgs_.stdenvNoCC.mkDerivation {
            pname = "investing-screener";
            version = "1.0.0";
            dontUnpack = true;
            dontBuild = true;
            dontConfigure = true;
            installPhase = ''
              mkdir -p $out/bin
              cat << 'EOF' > $out/bin/invest
              #!/bin/sh
              exec ${pkgs_.bun}/bin/bun run /home/chris/dev/quiver-hq/projects/tools/apps/investing/src/index.ts "$@"
              EOF
              chmod +x $out/bin/invest
              ln -s invest $out/bin/inv
            '';
          };
        };

      multicaPackage = system:
        let
          pkgs_ = pkgs.${system};
          version = "0.3.18";
          release =
            if system == "x86_64-linux" then {
              platform = "linux-amd64";
              hash = "sha256-9tdWCDAqsCi95w91TKnVUOrTMAwX+zPyTu+cU9BbeAA=";
            } else if system == "aarch64-darwin" then {
              platform = "darwin-arm64";
              hash = "sha256-cQcC6WBX9cOH0mNrbxCRgHobs8GrARse7nk3C3ErrA0=";
            } else
              throw "Unsupported Multica platform: ${system}";
        in
        {
          multica = pkgs_.stdenvNoCC.mkDerivation {
            pname = "multica";
            inherit version;
            src = pkgs_.fetchurl {
              url = "https://github.com/multica-ai/multica/releases/download/v${version}/multica-cli-${version}-${release.platform}.tar.gz";
              inherit (release) hash;
            };
            sourceRoot = ".";
            dontBuild = true;
            installPhase = ''
              runHook preInstall
              install -Dm755 multica $out/bin/multica
              install -Dm644 LICENSE $out/share/licenses/multica/LICENSE
              runHook postInstall
            '';
            meta = {
              description = "Managed agent platform CLI and local daemon";
              homepage = "https://github.com/multica-ai/multica";
              license = pkgs_.lib.licenses.asl20;
              mainProgram = "multica";
            };
          };
        };
     in
    {
      packages = forAllSystems (system:
        (allCmdPackages system)
        // (antigravityPackages system)
        // (investingScreenerPackage system)
        // (multicaPackage system)
      );

      # -- NIXOS & DARWIN SYSTEM CONFIGURATIONS -----------------------------
      nixosConfigurations."quiver-wsl" = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        specialArgs = { inherit inputs; };
        modules = [ 
          nixos-wsl.nixosModules.wsl
          ./nixos/hosts/wsl/configuration.nix 
        ];
      };

      # ASUS PN54 (Ryzen 5) – Niri desktop host
      nixosConfigurations."quiver-pn54" = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        specialArgs = { inherit inputs; };
        modules = [
          ./nixos/hosts/pn54/configuration.nix
        ];
      };

      darwinConfigurations."quiver-mac" = nix-darwin.lib.darwinSystem {
        system = "aarch64-darwin";
        specialArgs = { inherit inputs; };
        modules = [
          # Example of where you would put your Mac-specific config
          # ./nixos/hosts/mac/configuration.nix 

          # You would also import home-manager here for macOS
        ];
      };

      # -- DEVELOPMENT SHELL ------------------------------------------------
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShell {
          packages =
            (with pkgs.${system}; [
              go
              nodejs_22
              bun
              sqlite
              git-lfs
              unzip
              zip
              ffmpeg
              tmux
              uv
              (yt-dlp.override { javascriptSupport = false; })
              self.packages.${system}.investing-screener
              self.packages.${system}.multica
              inputs.agent-of-empires.packages.${system}.aoe-with-web
             ])
             ++ nixpkgs.lib.optionals (system == "x86_64-linux") [
               self.packages.${system}.antigravity-cli
               self.packages.${system}.antigravity-manager
               self.packages.${system}.antigravity-ide
             ];
          shellHook = ''
            echo "🛠️ Quiver HQ Environment is ready."
            if command -v gh >/dev/null 2>&1; then
              gh extension list | grep -q "github/gh-copilot" || gh extension install github/gh-copilot
            fi
          '';
        };
      });
    };
}
