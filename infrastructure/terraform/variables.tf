variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "estateos"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for multi-AZ resources"
  type        = list(string)
  default     = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "estateos"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "estateos_admin"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_cache_clusters" {
  description = "Number of Redis cache clusters"
  type        = number
  default     = 2
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "r6g.large.search"
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch data nodes"
  type        = number
  default     = 3
}

variable "mq_instance_type" {
  description = "Amazon MQ broker instance type"
  type        = string
  default     = "mq.m5.large"
}

variable "ecs_api_desired_count" {
  description = "Desired count for API ECS service"
  type        = number
  default     = 4
}

variable "ecs_worker_desired_count" {
  description = "Desired count for Celery worker ECS service"
  type        = number
  default     = 4
}

variable "ecs_nginx_desired_count" {
  description = "Desired count for Nginx ECS service"
  type        = number
  default     = 2
}

variable "domain_name" {
  description = "Primary domain name for CloudFront and ALB"
  type        = string
  default     = "estateos.app"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "ecr_backend_repository" {
  description = "ECR repository name for backend image"
  type        = string
  default     = "estateos/backend"
}

variable "ecr_frontend_repository" {
  description = "ECR repository name for frontend image"
  type        = string
  default     = "estateos/frontend"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project   = "EstateOS"
    ManagedBy = "Terraform"
  }
}
