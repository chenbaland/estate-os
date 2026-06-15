output "endpoint" {
  value = aws_db_instance.main.address
}

output "port" {
  value = aws_db_instance.main.port
}

output "password" {
  value     = random_password.db.result
  sensitive = true
}

output "instance_arn" {
  value = aws_db_instance.main.arn
}
