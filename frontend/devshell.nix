{
  mkShell,
  nodejs,
  flakeRoot ? null,
}:
mkShell {
  buildInputs = [ nodejs ];
  inputsFrom = if flakeRoot != null then [ flakeRoot ] else [ ];
  shellHook = ''
    if [ -n "$FLAKE_ROOT" ]; then
      cd "$FLAKE_ROOT"/frontend
    fi
    if [ -f "package.json" ]; then
      npm install
    else
      echo "WARN: package.json not present, not installing"
    fi
  '';
}
