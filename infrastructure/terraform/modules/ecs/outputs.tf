output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "api_service_name" {
  value = aws_ecs_service.api.name
}

output "worker_service_name" {
  value = aws_ecs_service.worker.name
}

output "beat_service_name" {
  value = aws_ecs_service.beat.name
}

output "nginx_service_name" {
  value = aws_ecs_service.nginx.name
}
