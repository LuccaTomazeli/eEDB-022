data "archive_file" "ingestion" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/../build/ingestion-lambda.zip"
}

resource "aws_lambda_function" "ingestion" {
  function_name    = var.ingestion_function_name
  role             = local.role_arn
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.ingestion.output_path
  source_code_hash = data.archive_file.ingestion.output_base64sha256

  environment {
    variables = {
      S3_BUCKET    = data.aws_s3_bucket.dados.bucket
      S3_KEY       = "entrada/bancos/EnquadramentoInicia_v2.json"
      SQS_QUEUE_URL = aws_sqs_queue.dados.url
    }
  }
}

resource "aws_lambda_function" "consumer" {
  function_name    = var.consumer_function_name
  role             = local.role_arn
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/../${var.consumer_package_path}"
  source_code_hash = filebase64sha256("${path.module}/../${var.consumer_package_path}")
  timeout          = 30

  environment {
    variables = {
      SQL_HOST          = var.sql_host
      SQL_PORT          = var.sql_port
      SQL_USER          = var.sql_user
      SQL_PASSWORD      = var.sql_password
      SQL_DATABASE      = var.sql_database
      S3_BUCKET         = data.aws_s3_bucket.dados.bucket
      S3_OUTPUT_PREFIX  = "processados"
      S3_ENRICHED_KEY   = "enriquecidos/dados_enriquecidos.json"
    }
  }

  dynamic "vpc_config" {
    for_each = length(var.subnet_ids) > 0 && length(var.security_group_ids) > 0 ? [true] : []
    content {
      subnet_ids         = var.subnet_ids
      security_group_ids = var.security_group_ids
    }
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3InvokeActivity6"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.dados.arn
  source_account = data.aws_caller_identity.current.account_id
}
