variable "cluster-node-count" {
  description = "How many node to spin up for the cluster to create node pool."
  default = 1
}

variable "digitalocean-cluster-tag" {
  description = "Add extra tags if you want; this can be useful if you plan to use DigitalOcean API or just to better organize your node pools."
  default = "production"
}

# CREDENTIALS

variable digitalocean_token {
    description = "If you don't have this, you can always create one in digitalocean UI, under settings. Note that the token will only show for once. Write this down and put in credentials.tfvars, make sure it's gitignored."
}
