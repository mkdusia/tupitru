{
  lib,
  python3,
  stdenvNoCC,
}:

let
  python = python3.withPackages (
    ps:
    with builtins;
    with lib;
    let
      allPkgs = pipe ./requirements.txt [
        builtins.readFile
        (splitString "\n")
        (map trim)
        (filter (s: s != ""))
        (filter (s: match "#.*" s == null))
        (map (splitString " "))
        (map head)
      ];
      basePkgs = pipe allPkgs [
        (map (splitString "["))
        (map (list: elemAt list 0))
        (map (name: ps."${name}"))
      ];
      optPkgs = pipe allPkgs [
        (map (builtins.match "([^\\[]*)\\[([^]]*)]"))
        (builtins.filter (s: s != null))
        (map (list: {
          name = elemAt list 0;
          set = elemAt list 1;
        }))
        (map ({ name, set }: ps."${name}".optional-dependencies."${set}"))
      ];
    in
    basePkgs ++ builtins.concatLists optPkgs
  );
in

stdenvNoCC.mkDerivation {
  name = "tupitru-backend";
  src = ./.;

  installPhase = ''
    mkdir -p "$out/bin"

    cat > "$out/bin/tupitru-backend-devel" <<-EOF
    #! ${stdenvNoCC.shell}
    cd $src
    ${python}/bin/fastapi dev main.py \$@
    EOF
    chmod 0755 "$out/bin/tupitru-backend-devel"

    cat > "$out/bin/tupitru-backend-prod" <<-EOF
    #! ${stdenvNoCC.shell}
    cd $src
    ${python}/bin/fastapi run main.py \$@
    EOF
    chmod 0755 "$out/bin/tupitru-backend-prod"
  '';

  propagatedBuildInputs = [ python ];
}
