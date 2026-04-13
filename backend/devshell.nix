{
  lib,
  mkShell,
  uv2nix,
  python313,
  callPackage,
  pyproject-nix,
  pyproject-build-systems,
  flakeRoot ? null,
}:

let
  workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

  python = python313;

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  pythonSet = (callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (
    lib.composeManyExtensions [
      pyproject-build-systems.overlays.default
      overlay
    ]
  );

  devVenv = pythonSet.mkVirtualEnv "tupitru-backend-dev-env" {
    tupitru-backend = [ "dev" ];
  };
in

mkShell {
  buildInputs = [ devVenv ];
  inputsFrom = if flakeRoot != null then [ flakeRoot ] else [ ];
  shellHook = ''
    if [ -n "$FLAKE_ROOT" ]; then
      cd "$FLAKE_ROOT"/backend
    fi
  '';
}
