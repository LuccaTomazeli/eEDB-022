resource "aws_sqs_queue" "dados" {
  name                       = var.queue_name
  visibility_timeout_seconds = 30

  lifecycle {
    ignore_changes = [max_message_size]
  }
}

resource "aws_lambda_event_source_mapping" "consumer" {
  event_source_arn        = aws_sqs_queue.dados.arn
  function_name           = aws_lambda_function.consumer.arn
  batch_size              = 10
  function_response_types = ["ReportBatchItemFailures"]
  enabled                 = true

  scaling_config {
    maximum_concurrency = 2
  }
}
