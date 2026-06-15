variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "redis_security_group_id" {
  type = string
}

variable "node_type" {
  type = string
}

variable "num_cache_clusters" {
  type = number
}

variable "tags" {
  type = map(string)
}
