locals {
  dockercfgjson = {
    "${var.docker_registry_server}" = {
      email    = "${var.docker_registry_email}"
      username = "${var.docker_registry_username}"
      password = "${var.docker_registry_password}"
    }
  }
}

resource "kubernetes_secret" "docker-registry-secrets" {
  metadata {
    name = "docker-registry-secrets"
    # namespace = "${kubernetes_namespace.blog.metadata.0.name}"
  }

  data = {
    ".dockercfgjson" = "${ jsonencode(local.dockercfgjson) }"
  }

  type = "kubernetes.io/dockercfgjson"
}