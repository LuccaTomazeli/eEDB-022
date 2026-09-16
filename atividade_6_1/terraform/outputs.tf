output "bucket_name" {
  value = data.aws_s3_bucket.dados.bucket
}

output "queue_url" {
  value = aws_sqs_queue.dados.url
}

output "queue_arn" {
  value = aws_sqs_queue.dados.arn
}

output "ingestion_function_arn" {
  value = aws_lambda_function.ingestion.arn
}

output "consumer_function_arn" {
  value = aws_lambda_function.consumer.arn
}

output "lambda_role_arn" {
  value = local.role_arn
}
