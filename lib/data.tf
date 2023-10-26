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

# Terraform data blocks

data "newrelic_entity" "app_1" {
  name   = "platform-auth-api"
  domain = "APM"
}


output "platform-auth-api" {
  value = {
    guid           = data.newrelic_entity.app_1.guid
    application_id = data.newrelic_entity.app_1.application_id
  }
}


data "newrelic_entity" "app_2" {
  name   = "pj-submission-auth-client-api"
  domain = "APM"
}


output "pj-submission-auth-client-api" {
  value = {
    guid           = data.newrelic_entity.app_2.guid
    application_id = data.newrelic_entity.app_2.application_id
  }
}


data "newrelic_entity" "app_3" {
  name   = "pj-submission-journal-config-api"
  domain = "APM"
}


output "pj-submission-journal-config-api" {
  value = {
    guid           = data.newrelic_entity.app_3.guid
    application_id = data.newrelic_entity.app_3.application_id
  }
}


data "newrelic_entity" "app_4" {
  name   = "pj-submission-renderer-api"
  domain = "APM"
}


output "pj-submission-renderer-api" {
  value = {
    guid           = data.newrelic_entity.app_4.guid
    application_id = data.newrelic_entity.app_4.application_id
  }
}


data "newrelic_entity" "app_5" {
  name   = "pj-submission-metadata-ro-api"
  domain = "APM"
}


output "pj-submission-metadata-ro-api" {
  value = {
    guid           = data.newrelic_entity.app_5.guid
    application_id = data.newrelic_entity.app_5.application_id
  }
}


data "newrelic_entity" "app_6" {
  name   = "pj-submission-metadata-api"
  domain = "APM"
}


output "pj-submission-metadata-api" {
  value = {
    guid           = data.newrelic_entity.app_6.guid
    application_id = data.newrelic_entity.app_6.application_id
  }
}


data "newrelic_entity" "app_7" {
  name   = "pj-submission-storage-api"
  domain = "APM"
}


output "pj-submission-storage-api" {
  value = {
    guid           = data.newrelic_entity.app_7.guid
    application_id = data.newrelic_entity.app_7.application_id
  }
}


data "newrelic_entity" "app_8" {
  name   = "pj-submission-notifications-api"
  domain = "APM"
}


output "pj-submission-notifications-api" {
  value = {
    guid           = data.newrelic_entity.app_8.guid
    application_id = data.newrelic_entity.app_8.application_id
  }
}


data "newrelic_entity" "app_9" {
  name   = "pj-submission-events-notification-api"
  domain = "APM"
}


output "pj-submission-events-notification-api" {
  value = {
    guid           = data.newrelic_entity.app_9.guid
    application_id = data.newrelic_entity.app_9.application_id
  }
}


data "newrelic_entity" "app_10" {
  name   = "pj-submission-transfer-api"
  domain = "APM"
}


output "pj-submission-transfer-api" {
  value = {
    guid           = data.newrelic_entity.app_10.guid
    application_id = data.newrelic_entity.app_10.application_id
  }
}


data "newrelic_entity" "app_11" {
  name   = "cats-website-ui"
  domain = "APM"
}


output "cats-website-ui" {
  value = {
    guid           = data.newrelic_entity.app_11.guid
    application_id = data.newrelic_entity.app_11.application_id
  }
}


data "newrelic_entity" "app_12" {
  name   = "cats-website-ui-uat"
  domain = "APM"
}


output "cats-website-ui-uat" {
  value = {
    guid           = data.newrelic_entity.app_12.guid
    application_id = data.newrelic_entity.app_12.application_id
  }
}


data "newrelic_entity" "app_13" {
  name   = "dap-me-articlecategory-api"
  domain = "APM"
}


output "dap-me-articlecategory-api" {
  value = {
    guid           = data.newrelic_entity.app_13.guid
    application_id = data.newrelic_entity.app_13.application_id
  }
}


data "newrelic_entity" "app_14" {
  name   = "pj-asc-ecs-api"
  domain = "APM"
}


output "pj-asc-ecs-api" {
  value = {
    guid           = data.newrelic_entity.app_14.guid
    application_id = data.newrelic_entity.app_14.application_id
  }
}


data "newrelic_entity" "app_15" {
  name   = "pj-asc-dashboard-api"
  domain = "APM"
}


output "pj-asc-dashboard-api" {
  value = {
    guid           = data.newrelic_entity.app_15.guid
    application_id = data.newrelic_entity.app_15.application_id
  }
}


data "newrelic_entity" "app_16" {
  name   = "customers-api"
  domain = "APM"
}


output "customers-api" {
  value = {
    guid           = data.newrelic_entity.app_16.guid
    application_id = data.newrelic_entity.app_16.application_id
  }
}


data "newrelic_entity" "app_17" {
  name   = "customers-api-uat"
  domain = "APM"
}


output "customers-api-uat" {
  value = {
    guid           = data.newrelic_entity.app_17.guid
    application_id = data.newrelic_entity.app_17.application_id
  }
}


data "newrelic_entity" "app_18" {
  name   = "orders-api"
  domain = "APM"
}


output "orders-api" {
  value = {
    guid           = data.newrelic_entity.app_18.guid
    application_id = data.newrelic_entity.app_18.application_id
  }
}


data "newrelic_entity" "app_19" {
  name   = "pj-rd-dashboard-ui"
  domain = "APM"
}


output "pj-rd-dashboard-ui" {
  value = {
    guid           = data.newrelic_entity.app_19.guid
    application_id = data.newrelic_entity.app_19.application_id
  }
}


data "newrelic_entity" "app_20" {
  name   = "pcm-products-api"
  domain = "APM"
}


output "pcm-products-api" {
  value = {
    guid           = data.newrelic_entity.app_20.guid
    application_id = data.newrelic_entity.app_20.application_id
  }
}


data "newrelic_entity" "app_21" {
  name   = "pj-rd-articlesearch-api"
  domain = "APM"
}


output "pj-rd-articlesearch-api" {
  value = {
    guid           = data.newrelic_entity.app_21.guid
    application_id = data.newrelic_entity.app_21.application_id
  }
}

