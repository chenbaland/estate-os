variable "name_prefix" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "certificate_arn" {
  type    = string
  default = ""
}

variable "s3_bucket_id" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "alb_dns_name" {
  type = string
}

variable "tags" {
  type = map(string)
}
