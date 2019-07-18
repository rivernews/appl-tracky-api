locals {
  dockercfg = {
    "${var.docker_registry_server}" = {
      email    = "${var.docker_registry_email}"
      username = "${var.docker_registry_username}"
      password = "${var.docker_registry_password}"
    }
  }
}

