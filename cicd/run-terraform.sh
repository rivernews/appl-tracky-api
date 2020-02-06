#!/usr/bin/env bash

# tf remote backend types doc: https://www.terraform.io/docs/backends/types/pg.html
# tf partial backend config: https://www.terraform.io/docs/backends/config.html
# tf doc env var: https://www.terraform.io/docs/configuration/variables.html#environment-variables

# use s3 for remote state

# for avoiding secrets recorded in shell history
# https://unix.stackexchange.com/a/10923
set +o history
terraform init \
    -backend-config="access_key=${TF_VAR_aws_access_key}" \
    -backend-config="secret_key=${TF_VAR_aws_secret_key}" \
    -backend-config="region=${TF_BACKEND_region}"
set -o history

terraform validate

terraform plan -var="app_container_image_tag=${CIRCLE_SHA1}"

terraform apply -auto-approve -var="app_container_image_tag=${CIRCLE_SHA1}"
