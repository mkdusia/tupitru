{
  frontend,
  backend,
}:
{
  lib,
  config,
  options,
  ...
}:
let
  inherit (lib) mkOption types literalExpression;

  this = config.services.tupitru;
in
{
  options = {
    services.tupitru = {
      enable = lib.mkEnableOption "the Tupitru! backend & frontend service, via nginx reverse-proxy.";
      backend = {
        enable = mkOption {
          default = this.enable;
          defaultText = "services.tupitru.enable";
          example = true;
          type = types.bool;
          description = "Whether to run the Tupitru application backend.";
        };
        package = lib.mkOption {
          default = backend;
          example = literalExpression "pkgs.my-tupitru-backend";
          type = types.package;
          description = "Backend package to use. It must provide the tupitru-backend-prod binary.";
        };
        port = mkOption {
          type = types.port;
          default = 38689;
          example = 24601;
          description = "The port number on which to serve the backend.";
        };
        workers = mkOption {
          type = types.nullOr types.ints.positive;
          default = null;
          example = 4;
          description = "The suggested number of workers passed through to the backend server.";
        };
        host = mkOption {
          type = types.str;
          default = "127.0.0.1";
          example = "0.0.0.0";
          description = ''
            To which addresses should the backend server bind to.
            Defaults due to the expected use of reverse-proxy.
          '';
        };
        extraFlags = mkOption {
          type = types.str;
          default = "";
          example = "--no-proxy-headers";
          description = "Additional flags passed through to the backend server.";
        };
      };
      frontend = {
        package = lib.mkOption {
          default = frontend;
          example = literalExpression "pkgs.my-tupitru-frontend";
          type = types.package;
          description = "Compiled frontend package to serve via the proxy.";
        };
      };
      hostname = lib.mkOption {
        example = "tupitru.example.com";
        type = types.str;
        description = "Hostname for the Tupitru! frontend & backend to be served on";
      };

      forceSSL = lib.mkOption {
        type = types.bool;
        default = config.services.tupitru.hostname != "localhost";
        defaultText = literalExpression "config.services.tupitru.hostname != \"localhost\"";
        example = false;
        description = "Whether to force users to use HTTPS by redirecting them from the HTTP port.";
      };
      nginxExtras = lib.mkOption {
        type = options.services.nginx.virtualHosts.type.nestedTypes.elemType;
        default = { };
        example = {
          acmeRoot = "tupitru";
        };
        description = "Additional options to pass through to the services.nginx.virtualHosts.<hostname> field";
      };
    };
  };
  config = {
    services.nginx = lib.mkIf this.enable {
      enable = lib.mkDefault true;
      virtualHosts."${this.hostname}" = this.nginxExtras // {
        inherit (this) forceSSL;
        locations = {
          "/" = {
            root = "${this.frontend.package}";
          };
          "/ws" = {
            recommendedProxySettings = true;
            proxyWebsockets = true;
            proxyPass = "http://localhost:${toString this.backend.port}";
          };
        };
      };
    };
    systemd.services = lib.mkIf this.enable {
      tupitru-backend = {
        description = "Tupitru! server backend";

        wantedBy = [ "multi-user.target" ];
        serviceConfig = {
          DynamicUser = true;
          PrivateTmp = true;
          NoNewPrivileges = true;
          MemoryDenyWriteExecute = true;
          RuntimeDirectory = "tupitru-backend";

          ExecStart =
            "${this.backend.package}/bin/tupitru-backend-prod --host ${this.backend.host} --port ${toString this.backend.port} "
            + (if this.backend.workers != null then "--workers ${this.backend.workers} " else "")
            + this.backend.extraFlags;
        };
      };
    };
  };
}
