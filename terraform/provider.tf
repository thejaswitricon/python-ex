# Configure the terraform and New Relic provider versions
# More details: https://www.terraform.io/docs/configuration/provider-requirements.html
# https://github.com/newrelic/terraform-provider-newrelic/blob/main/CHANGELOG.md

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = ">= 1.0.0"
    }
    newrelic = {
      source  = "newrelic/newrelic"
      version = ">= 3.25.0"
    }
  }
}
