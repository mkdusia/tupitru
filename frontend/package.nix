let
  mkPackage =
    {
      backendHost ? "localhost",
      useWSS ? false,

      buildNpmPackage,
      nodejs,
      importNpmLock,
    }@attrs:
    let
      backendUrl = "ws${if useWSS then "s" else ""}://${backendHost}/ws";
    in
    buildNpmPackage {
      passthru = {
        withConfig =
          {
            backendHost ? "localhost",
            useWSS ? false,
          }@args:
          mkPackage (attrs // args);
      };

      pname = "tupitru-frontend";
      inherit ((builtins.fromJSON (builtins.readFile ./package.json))) version;
      inherit (importNpmLock) npmConfigHook;
      inherit (attrs) nodejs;

      VITE_BASE_URL = backendUrl;

      src = ./.;
      preBuild = ''
        cp ${../rules.md} ../rules.md
      '';
      npmDeps = importNpmLock {
        npmRoot = ./.;
      };
      installPhase = ''
        mkdir -p $out
        cp -r ./dist/* $out/
      '';
    };
in
mkPackage
