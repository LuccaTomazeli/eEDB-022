terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_network" "atividade8" {
  name = "atividade8_default"
}

resource "docker_container" "postgres" {
  name  = "atividade8-postgres-terraform"
  image = "postgres:16-alpine"
  networks_advanced { name = docker_network.atividade8.name }
  env = ["POSTGRES_DB=atividade8", "POSTGRES_USER=atividade8", "POSTGRES_PASSWORD=atividade8"]
  ports {
    internal = 5432
    external = 5432
  }
}