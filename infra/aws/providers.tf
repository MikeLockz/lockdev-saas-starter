terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # aptible = {
    #   source  = "aptible/aptible"
    #   version = "~> 0.1"
    # }
    # twilio = {
    #   source  = "twilio/twilio"
    #   version = "~> 0.1"
    # }
  }
}

provider "aws" {
  region = var.aws_region
}
