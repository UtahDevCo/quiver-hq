{ config, pkgs, ... }:

{
  # 1. Ensure Docker is enabled
  virtualisation.docker.enable = true;
  virtualisation.oci-containers.backend = "docker";

  # 2. Fizzy Docker Container

  virtualisation.oci-containers.containers."fizzy" = {
    image = "ghcr.io/basecamp/fizzy:main";
    ports = [ "7890:80" ];
    volumes = [
      "/home/chris/fizzy/storage:/rails/storage"
    ];
    environmentFiles = [
      "/home/chris/fizzy/.env"
    ];
  };

  # 3. Cloudflare Tunnel Service
  services.cloudflared = {
    enable = true;
    tunnels = {
      "92fa1834-368c-4a26-b386-848542a31e99" = {
        credentialsFile = "/home/chris/.cloudflared/92fa1834-368c-4a26-b386-848542a31e99.json";
        ingress = {
          "fizzy.chrisesplin.com" = "http://localhost:7890";
        };
        default = "http_status:404";
      };
    };
  };
}
