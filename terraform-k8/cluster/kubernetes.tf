provider "kubernetes" {
  host = "${data.digitalocean_kubernetes_cluster.project-cluster.endpoint}"

  client_certificate     = "${base64decode(data.digitalocean_kubernetes_cluster.project-cluster.kube_config.0.client_certificate)}"
  client_key             = "${base64decode(data.digitalocean_kubernetes_cluster.project-cluster.kube_config.0.client_key)}"
  cluster_ca_certificate = "${base64decode(data.digitalocean_kubernetes_cluster.project-cluster.kube_config.0.cluster_ca_certificate)}"
}

# You can now cd in this module directory and run `kubectl --kubeconfig kubeconfig.yaml get sa` to get service account list.
resource "local_file" "kubeconfig" {
    content     = "${digitalocean_kubernetes_cluster.project-cluster.kube_config.0.raw_config}"
    filename = "kubeconfig.yaml"
}