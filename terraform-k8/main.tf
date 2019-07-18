module "cluster" {
  source = "./cluster"
  
  # variables for such module
  digitalocean_token = "${var.digitalocean_token}"
}
