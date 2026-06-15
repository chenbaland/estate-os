terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    bucket         = "estateos-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "estateos-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(var.tags, {
      Environment = var.environment
    })
  }
}

data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = merge(var.tags, {
    Environment = var.environment
    Project     = var.project_name
  })
}

# Networking
module "vpc" {
  source = "./modules/vpc"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  tags               = local.common_tags
}

# Data stores
module "rds" {
  source = "./modules/rds"

  name_prefix          = local.name_prefix
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  db_security_group_id = module.vpc.rds_security_group_id
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  db_name              = var.db_name
  db_username          = var.db_username
  tags                 = local.common_tags
}

module "elasticache" {
  source = "./modules/elasticache"

  name_prefix            = local.name_prefix
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  redis_security_group_id = module.vpc.redis_security_group_id
  node_type              = var.redis_node_type
  num_cache_clusters     = var.redis_num_cache_clusters
  tags                   = local.common_tags
}

module "amazon_mq" {
  source = "./modules/amazon_mq"

  name_prefix              = local.name_prefix
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  mq_security_group_id     = module.vpc.mq_security_group_id
  instance_type            = var.mq_instance_type
  tags                     = local.common_tags
}

module "opensearch" {
  source = "./modules/opensearch"

  name_prefix                 = local.name_prefix
  vpc_id                      = module.vpc.vpc_id
  private_subnet_ids          = module.vpc.private_subnet_ids
  opensearch_security_group_id = module.vpc.opensearch_security_group_id
  instance_type               = var.opensearch_instance_type
  instance_count              = var.opensearch_instance_count
  tags                        = local.common_tags
}

# Storage & CDN
module "s3" {
  source = "./modules/s3"

  name_prefix = local.name_prefix
  tags        = local.common_tags
}

# Load balancing
module "alb" {
  source = "./modules/alb"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.vpc.alb_security_group_id
  certificate_arn       = var.certificate_arn
  tags                  = local.common_tags
}

module "cloudfront" {
  source = "./modules/cloudfront"

  name_prefix     = local.name_prefix
  domain_name     = var.domain_name
  certificate_arn = var.certificate_arn
  s3_bucket_id    = module.s3.static_bucket_id
  s3_bucket_arn   = module.s3.static_bucket_arn
  alb_dns_name    = module.alb.alb_dns_name
  tags            = local.common_tags
}

# Container orchestration
module "ecs" {
  source = "./modules/ecs"

  name_prefix              = local.name_prefix
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  ecs_security_group_id    = module.vpc.ecs_security_group_id
  target_group_arn         = module.alb.target_group_arn
  ecr_backend_repository   = var.ecr_backend_repository
  ecr_frontend_repository  = var.ecr_frontend_repository
  image_tag                = var.image_tag
  api_desired_count        = var.ecs_api_desired_count
  worker_desired_count     = var.ecs_worker_desired_count
  nginx_desired_count      = var.ecs_nginx_desired_count
  db_host                  = module.rds.endpoint
  db_name                  = var.db_name
  db_username              = var.db_username
  db_password              = module.rds.password
  redis_endpoint           = module.elasticache.endpoint
  mq_endpoint              = module.amazon_mq.endpoint
  opensearch_endpoint      = module.opensearch.endpoint
  s3_bucket_name           = module.s3.media_bucket_id
  aws_region               = var.aws_region
  tags                     = local.common_tags
}
