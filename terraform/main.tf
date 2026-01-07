terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source to get current AWS account ID
data "aws_caller_identity" "current" {}

# S3 bucket for artifacts
resource "aws_s3_bucket" "tdg_artifacts" {
  bucket = "tdg-artefacts-${data.aws_caller_identity.current.account_id}-${var.aws_region}"
}

resource "aws_s3_bucket_versioning" "tdg_artifacts_versioning" {
  bucket = aws_s3_bucket.tdg_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "tdg_artifacts_pab" {
  bucket = aws_s3_bucket.tdg_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Archive the Lib directory
data "archive_file" "lib_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../Lib"
  output_path = "${path.module}/lib.zip"
}

# Archive the Glue directory
data "archive_file" "glue_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../Glue"
  output_path = "${path.module}/glue.zip"
}

# Upload Lib files to S3
resource "aws_s3_object" "lib_files" {
  bucket = aws_s3_bucket.tdg_artifacts.id
  key    = "tgd_lib/TestDataGeneratorLib.py"
  source = "${path.module}/../Lib/TestDataGeneratorLib.py"
  etag   = filemd5("${path.module}/../Lib/TestDataGeneratorLib.py")
}

resource "aws_s3_object" "targ_files" {
  bucket = aws_s3_bucket.tdg_artifacts.id
  key    = "tgd_lib/TestDataGeneratorTarg.py"
  source = "${path.module}/../Lib/TestDataGeneratorTarg.py"
  etag   = filemd5("${path.module}/../Lib/TestDataGeneratorTarg.py")
}

# Upload Glue job script
resource "aws_s3_object" "glue_job_script" {
  bucket = aws_s3_bucket.tdg_artifacts.id
  key    = "tgd_glue_job/Job/TDGGlueJob.py"
  source = "${path.module}/../Glue/Job/TDGGlueJob.py"
  etag   = filemd5("${path.module}/../Glue/Job/TDGGlueJob.py")
}

# Upload configuration file
resource "aws_s3_object" "config_file" {
  bucket = aws_s3_bucket.tdg_artifacts.id
  key    = "tgd_glue_job/Config/TDG_configuration_file.yml"
  source = "${path.module}/../Glue/Config/TDG_configuration_file.yml"
  etag   = filemd5("${path.module}/../Glue/Config/TDG_configuration_file.yml")
}

# IAM role for Glue job
resource "aws_iam_role" "tdg_glue_role" {
  name = "TDG_Glue_Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.tdg_glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy_attachment" "s3_full_access" {
  role       = aws_iam_role.tdg_glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "dynamodb_full_access" {
  role       = aws_iam_role.tdg_glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# Custom IAM policy for additional permissions
resource "aws_iam_policy" "tdg_glue_policy" {
  name        = "TDG_Glue_Role_policy"
  description = "Custom policy for TDG Glue job"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.tdg_artifacts.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "tdg_custom_policy" {
  role       = aws_iam_role.tdg_glue_role.name
  policy_arn = aws_iam_policy.tdg_glue_policy.arn
}

# Glue job
resource "aws_glue_job" "tdg_job" {
  name         = "TestDataGeneratorJob"
  description  = "Test Data Generator main Glue job"
  role_arn     = aws_iam_role.tdg_glue_role.arn
  glue_version = "4.0"

  command {
    script_location = "s3://${aws_s3_bucket.tdg_artifacts.bucket}/tgd_glue_job/Job/TDGGlueJob.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--enable-metrics"                   = ""
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${aws_s3_bucket.tdg_artifacts.bucket}/sparkHistoryLogs/"
    "--enable-job-insights"              = "false"
    "--enable-observability-metrics"     = "true"
    "--enable-glue-datacatalog"          = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--config_file_path"                 = "${aws_s3_bucket.tdg_artifacts.bucket}/tgd_glue_job/Config/TDG_configuration_file.yml"
    "--extra-py-files"                   = "s3://${aws_s3_bucket.tdg_artifacts.bucket}/tgd_lib/TestDataGeneratorLib.py,s3://${aws_s3_bucket.tdg_artifacts.bucket}/tgd_lib/TestDataGeneratorTarg.py"
    "--extra-files"                      = "s3://${aws_s3_bucket.tdg_artifacts.bucket}/tgd_glue_job/Config/TDG_configuration_file.yml"
  }

  max_retries = 0
  timeout     = 2880
  
  depends_on = [
    aws_s3_object.lib_files,
    aws_s3_object.targ_files,
    aws_s3_object.glue_job_script,
    aws_s3_object.config_file
  ]
}