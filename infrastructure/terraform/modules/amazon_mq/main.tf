resource "random_password" "mq" {
  length  = 24
  special = false
}

resource "aws_mq_broker" "main" {
  broker_name = "${var.name_prefix}-rabbitmq"

  engine_type        = "RabbitMQ"
  engine_version     = "3.13"
  host_instance_type = var.instance_type
  deployment_mode    = "CLUSTER_MULTI_AZ"

  publicly_accessible = false
  subnet_ids          = slice(var.private_subnet_ids, 0, min(2, length(var.private_subnet_ids)))
  security_groups     = [var.mq_security_group_id]

  user {
    username = "estateos"
    password = random_password.mq.result
  }

  logs {
    general = true
  }

  maintenance_window_start_time {
    day_of_week = "SUNDAY"
    time_of_day = "04:00"
    time_zone   = "UTC"
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rabbitmq"
  })
}
