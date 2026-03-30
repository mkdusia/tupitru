{
  mkShell,
  callPackage,
  flakeRoot ? null,
}:
mkShell {
  buildInputs = [
    (callPackage ./package.nix { })
  ];
  inputsFrom = if flakeRoot != null then [ flakeRoot ] else [ ];
  shellHook = ''
    if [ -n "$FLAKE_ROOT" ]; then
      cd "$FLAKE_ROOT"/backend
    fi
  '';
}
