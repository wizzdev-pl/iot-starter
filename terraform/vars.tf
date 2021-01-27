variable "mode" {
  type = string
  description = "production or devel"
}

variable "region" {
  type = string
  description = "AWS region, ex. eu-west-2"
}

variable "default_tags" {
  type = map
  default = {
    created_by = "terraform"
  }
}

variable "project" {
  type = string
  description = "Tag: Name of project"
  default = "Not Provided"
}

variable "owner" {
  type = string
  description = "Tag: Mail of administrator"
  default = "Not Provided"
}

variable "ESP_HARD_PASSWORD" {
  description = "Constant password to connect from ESP"
  type = string
}

variable "ESP_HARD_LOGIN" {
  description = "Constant password to connect from ESP"
  type = string
}