{
  lib,
  stdenvNoCC,
  callPackage,
  python313,
  uv2nix,
  pyproject-nix,
  pyproject-build-systems,
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

  venv = pythonSet.mkVirtualEnv "tupitru-backend-env" workspace.deps.default;

  devVenv = pythonSet.mkVirtualEnv "tupitru-backend-dev-env" {
    tupitru-backend = [ "dev" ];
  };
in

stdenvNoCC.mkDerivation {
  name = "tupitru-backend";
  src = ./.;

  doCheck = true;

  checkPhase = ''
    runHook preCheck
    ${devVenv}/bin/ruff format --check .
    ${devVenv}/bin/ruff check .
    ${devVenv}/bin/pytest
    ${devVenv}/bin/mypy .
    runHook postCheck
  '';

  installPhase = ''
    mkdir -p "$out/bin"

    cat > "$out/bin/tupitru-backend-devel" <<-EOF
    #! ${stdenvNoCC.shell}
    cd $src
    ${venv}/bin/fastapi dev app/main.py \$@
    EOF
    chmod 0755 "$out/bin/tupitru-backend-devel"

    cat > "$out/bin/tupitru-backend-prod" <<-EOF
    #! ${stdenvNoCC.shell}
    cd $src
    ${venv}/bin/fastapi run app/main.py \$@
    EOF
    chmod 0755 "$out/bin/tupitru-backend-prod"
  '';

  passthru = {
    inherit venv devVenv;
  };
}
