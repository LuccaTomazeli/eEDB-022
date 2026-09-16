variable "region" {
  description = "Regiao AWS usada pelos recursos."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome globalmente unico do bucket de entrada e saida."
  type        = string
  default     = ""
}

variable "queue_name" {
  description = "Nome da fila SQS."
  type        = string
  default     = "atividade-6-1-fila"
}

variable "ingestion_function_name" {
  type    = string
  default = "atividade-6-1-ingestao"
}

variable "consumer_function_name" {
  type    = string
  default = "atividade-6-1-consumidor-sql"
}

variable "lambda_role_arn" {
  description = "ARN de uma role existente. Vazio usa a LabRole da conta."
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnets privadas da VPC do RDS para a Lambda consumidora."
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Security groups da Lambda consumidora."
  type        = list(string)
  default     = []
}

variable "sql_host" {
  type      = string
  sensitive = true
}

variable "sql_user" {
  type      = string
  sensitive = true
}

variable "sql_password" {
  type      = string
  sensitive = true
}

variable "sql_database" {
  type      = string
  sensitive = true
}

variable "sql_port" {
  type    = string
  default = "3306"
}

variable "consumer_package_path" {
  description = "ZIP produzido por scripts/package_lambdas.py."
  type        = string
  default     = "build/consumer-lambda.zip"
}
