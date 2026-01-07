output "s3_bucket_name" {
  description = "Name of the S3 bucket created for artifacts"
  value       = aws_s3_bucket.tdg_artifacts.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket created for artifacts"
  value       = aws_s3_bucket.tdg_artifacts.arn
}

output "glue_job_name" {
  description = "Name of the Glue job created"
  value       = aws_glue_job.tdg_job.name
}

output "glue_job_arn" {
  description = "ARN of the Glue job created"
  value       = aws_glue_job.tdg_job.arn
}

output "iam_role_name" {
  description = "Name of the IAM role created for Glue job"
  value       = aws_iam_role.tdg_glue_role.name
}

output "iam_role_arn" {
  description = "ARN of the IAM role created for Glue job"
  value       = aws_iam_role.tdg_glue_role.arn
}

output "config_file_path" {
  description = "S3 path to the configuration file"
  value       = "s3://${aws_s3_bucket.tdg_artifacts.bucket}/tgd_glue_job/Config/TDG_configuration_file.yml"
}