
terraform {
  required_version = ">= 1.0.0"

  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = pathexpand("~/.kube/config")
  }
}

variable "release_name" {
  description = "Existing NEXVION Helm release"
  type        = string
  default     = "nexvion"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "default"
}

resource "helm_release" "nexvion" {
  name      = var.release_name
  namespace = var.namespace
  chart     = "${path.module}/../helm/nexvion"

  values = [
    file("${path.module}/../helm/nexvion/values.yaml")
  ]

  wait    = true
  timeout = 180
}
