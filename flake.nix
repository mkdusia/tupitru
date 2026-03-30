{
  description = "Tupitru! – the fun animal block-sliding game";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-root.url = "github:srid/flake-root";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { withSystem, moduleWithSystem, ... }:
      {
        systems = [
          "x86_64-linux"
          "aarch64-linux"
          # "aarch64-darwin"
          # "x86_64-darwin"
        ];
        imports = [
          inputs.flake-root.flakeModule
        ];
        perSystem =
          {
            pkgs,
            config,
            ...
          }:
          {
            devShells.frontend = pkgs.callPackage ./frontend/devshell.nix {
              flakeRoot = config.flake-root.devShell;
            };
            devShells.backend = pkgs.callPackage ./backend/devshell.nix {
              flakeRoot = config.flake-root.devShell;
            };

            packages.frontend = pkgs.callPackage ./frontend/package.nix { };
            packages.backend = pkgs.callPackage ./backend/package.nix { };
          };
        flake = rec {
          nixosModules = rec {
            default = tupitru;
            tupitru = moduleWithSystem (
              { self', lib, ... }:
              _: {
                imports = [
                  (import ./module.nix {
                    inherit (self'.packages) frontend backend;
                  })
                ];
              }
            );
          };

          nixosConfigurations.container = withSystem "x86_64-linux" (
            {
              config,
              inputs',
              self',
              ...
            }:
            inputs.nixpkgs.lib.nixosSystem {
              system = "x86_64-linux";

              modules = [
                {
                  boot.isNspawnContainer = true;
                  networking.firewall.allowedTCPPorts = [ 80 ];
                  system.stateVersion = "25.11";
                }
                nixosModules.tupitru
                {
                  services.tupitru.enable = true;
                  services.tupitru.hostname = "localhost";
                }
              ];
            }
          );
        };
      }
    );
}
