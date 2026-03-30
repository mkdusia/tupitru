{
  buildNpmPackage,
  bash,
  nodejs,
  importNpmLock,
}@attrs:
buildNpmPackage {
  pname = "tupitru-frontend";
  inherit ((builtins.fromJSON (builtins.readFile ./package.json))) version;
  inherit (importNpmLock) npmConfigHook;
  inherit (attrs) nodejs;

  src = ./.;
  npmDeps = importNpmLock {
    npmRoot = ./.;
  };
  installPhase = ''
    mkdir -p $out
    cp -r ./dist/* $out/
  '';
}
