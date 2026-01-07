# Terraform Deployment for AWS Glue Test Data Generator

This directory contains Terraform configuration files to deploy the AWS Glue Test Data Generator infrastructure.

## Prerequisites

1. **Terraform**: Install Terraform >= 1.0
   ```bash
   # Download from https://www.terraform.io/downloads.html
   # Or use package manager:
   # Windows (Chocolatey): choco install terraform
   # macOS (Homebrew): brew install terraform
   # Linux (Ubuntu): sudo apt-get install terraform
   ```

2. **AWS CLI**: Configure AWS credentials
   ```bash
   aws configure
   ```

3. **AWS Permissions**: Ensure your AWS credentials have permissions for:
   - S3 (create buckets, upload objects)
   - IAM (create roles, policies)
   - AWS Glue (create jobs)
   - CloudWatch Logs

## Quick Start

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Configure Variables (Optional)
```bash
# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your preferred settings
# aws_region = "us-west-2"  # Change to your preferred region
```

### 3. Plan Deployment
```bash
terraform plan
```

### 4. Deploy Infrastructure
```bash
terraform apply
```

### 5. Verify Deployment
After successful deployment, you'll see outputs including:
- S3 bucket name for artifacts
- Glue job name and ARN
- IAM role details

## Configuration Files

| File | Description |
|------|-------------|
| `main.tf` | Main Terraform configuration with all resources |
| `variables.tf` | Input variables definition |
| `outputs.tf` | Output values after deployment |
| `terraform.tfvars.example` | Example variables file |

## Resources Created

The Terraform configuration creates the following AWS resources:

### 🪣 S3 Resources
- **S3 Bucket**: `tdg-artefacts-{account-id}-{region}`
  - Versioning enabled
  - Public access blocked
  - Contains Python libraries and configuration files

### 👤 IAM Resources
- **IAM Role**: `TDG_Glue_Role`
  - Trusted by AWS Glue service
  - Attached policies:
    - `AWSGlueServiceRole` (AWS managed)
    - `AmazonS3FullAccess` (AWS managed)
    - `AmazonDynamoDBFullAccess` (AWS managed)
    - `TDG_Glue_Role_policy` (custom policy)

### ⚙️ AWS Glue Resources
- **Glue Job**: `TestDataGeneratorJob`
  - Python 3.x runtime
  - Glue version 4.0
  - Configured with required libraries and configuration file

## Customization

### Change AWS Region
```bash
# In terraform.tfvars
aws_region = "eu-west-1"
```

### Add Custom Tags
```bash
# In terraform.tfvars
tags = {
  Project     = "My Data Generator"
  Environment = "production"
  ManagedBy   = "Terraform"
  Owner       = "DataTeam"
  CostCenter  = "Analytics"
}
```

### Modify Glue Job Settings
Edit `main.tf` in the `aws_glue_job` resource to customize:
- `timeout`: Job timeout in minutes
- `max_retries`: Maximum retry attempts
- `default_arguments`: Additional Glue job arguments

## Running the Glue Job

After deployment, you can run the job via:

### AWS Console
1. Go to AWS Glue Console
2. Navigate to **Jobs** under **Data Integration and ETL**
3. Select **TestDataGeneratorJob**
4. Click **Run job**

### AWS CLI
```bash
aws glue start-job-run --job-name TestDataGeneratorJob
```

### Terraform (Optional)
Add this resource to trigger job runs:
```hcl
resource "aws_glue_trigger" "tdg_trigger" {
  name = "tdg-manual-trigger"
  type = "ON_DEMAND"
  
  actions {
    job_name = aws_glue_job.tdg_job.name
  }
}
```

## Configuration Management

The configuration file is located at:
```
s3://{bucket-name}/tgd_glue_job/Config/TDG_configuration_file.yml
```

To update the configuration:
1. Modify `../Glue/Config/TDG_configuration_file.yml`
2. Run `terraform apply` to upload the updated file

## Cleanup

To destroy all created resources:
```bash
terraform destroy
```

⚠️ **Warning**: This will permanently delete all resources including the S3 bucket and any generated data.

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure AWS credentials have required permissions
   - Check IAM policies attached to your user/role

2. **Resource Already Exists**
   - S3 bucket names must be globally unique
   - Modify bucket naming in `main.tf` if needed

3. **Terraform State Issues**
   - Use `terraform refresh` to sync state
   - Consider using remote state for team environments

### Logs and Monitoring

- **Glue Job Logs**: Available in CloudWatch Logs
- **Spark UI**: Enabled for job debugging
- **Job Metrics**: Available in CloudWatch Metrics

