output "endpoint" {
  value = aws_mq_broker.main.instances[0].endpoints[0]
}

output "password" {
  value     = random_password.mq.result
  sensitive = true
}

output "broker_id" {
  value = aws_mq_broker.main.id
}
