data "aws_caller_identity" "current" {}

data "aws_iam_role" "lambda" {
  count = var.lambda_role_arn == "" ? 1 : 0
  name  = "LabRole"
}

locals {
  bucket_name = var.bucket_name != "" ? var.bucket_name : "atividade-6-1-${data.aws_caller_identity.current.account_id}"
  role_arn    = var.lambda_role_arn != "" ? var.lambda_role_arn : data.aws_iam_role.lambda[0].arn
}
