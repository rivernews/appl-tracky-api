provider "digitalocean" {
  token = "${var.digitalocean_token}"
}

resource "digitalocean_kubernetes_cluster" "project-cluster" {
  name = "${var.project_name}-cluster"
  region  = "sfo2"
  version = "1.14.3-do.0"
  tags    = ["${var.digitalocean-cluster-tag}"]

  node_pool {
    name       = "${var.project_name}-cluster-worker-pool"
    size       = "s-1vcpu-2gb"
    node_count = "${var.cluster-node-count}"
    tags       = ["${var.digitalocean-cluster-tag}"]
  }
}