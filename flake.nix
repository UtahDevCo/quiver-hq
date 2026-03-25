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
  };

  outputs = { self, nixpkgs, nixos-wsl, home-manager, nix-darwin, ... }@inputs:
    let
      # Define systems for which we want to build shells and packages
      supportedSystems = [ "x86_64-linux" "aarch64-darwin" ];

      # Helper function to generate package sets for each system
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Nixpkgs for each system
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
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
          packages = with pkgs.${system}; [
            go
            nodejs_22
            bun
            sqlite
          ];
          shellHook = ''
            echo "🛠️ Quiver HQ Environment is ready."
          '';
        };
      });
    };
}
