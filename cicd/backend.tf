terraform {
  backend "s3" {
    bucket = "iriversland-cloud"
    key    = "terraform/appl-tracky-api.remote-terraform.tfstate"
  }
}
