data "aws_s3_bucket" "dados" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_notification" "dados" {
  bucket = data.aws_s3_bucket.dados.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_prefix       = "entrada/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
