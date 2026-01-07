## AWS Glue Test Data Generator for S3 Data Lakes and DynamoDB
Test data generation plays a critical role in evaluating system performance, validating accuracy, bug identification, enhancing reliability, assessing scalability, ensuring regulatory compliance, training machine learning models, and supporting CI/CD processes. It enables the discovery of potential issues and ensures that systems operate as intended across diverse scenarios.

The AWS Glue Test Data Generator provides a configurable framework for Test Data Generation using AWS Glue Pyspark serverless Jobs. The required test data description is fully configurable through a YAML configuration file.

## Code Repository on Github
The source code and depolyment instruction are accessible through this link: [Github Code Repository](https://github.com/aws-samples/aws-glue-test-data-generator)

## Supported data types

The Test Data Generation Framework currently supports the following types:

* **Unique Key Generator**

  This generator produces formatted unique values that can be used as partition key. you can specify a prefix to and the number of leading zeros if required.

* **Child Key Generator**

  This generator produces a child key referencing the primary key. This is useful in generating multi-level hierarchical data. you can specify the number of levels and how many nodes you want to generate per level.

* **String Data Generator**

  This generator produces String data type with various mechanisms:

   * **Random Strings**: you can specify the number of characters and the type of generated characters: numeric, alphabetic or alphanumeric values. This can be used for generating random serial numbers, ordinal data, codes, identity numbers, .. etc.

  * **Strings from a Dictionary**: you can provide a dictionary of words to pick up randomly by the generator. This can be used to generate categorical columns with predefined set of values such as order status, product types, marital status, gender,..etc/

  * **Strings from a Pattern**: you can provide generic pattern for your string data. This can be used to generate fake emails, formatted phone numbers, comments, address like data, …etc.

* **Integer Data Generator** 

  This generator produces random integer data from a specified range.

* **Float/Double Data Generator** 

  This generator produces random float/double data from an expression. This can be used to generate float values such as salary, temperature, profit, statistical data,.. etc

* **Internet Address Data Generator** 

  This generator produces random IP addresses. This can be used to generate IP address ranges for testing applications used for internet traffic monitoring or filtering.


* **Date Data Generator**

  This generator produces random dates generator from a configurable date range.

* **Close Date Data Generator**

  This generator produces random from a configurable start date column and a range. This can be used to generate dates of specific intervals such as a support ticket close date, deceased date, expiration date,… etc

## Solution Architecture

![image](https://user-images.githubusercontent.com/17237690/219859235-924c127e-0c2d-40d3-837b-cb5c68aa2c45.png)

The Test Data Generator is based on PySpark library which is invoked through as a PySpark AWS Glue job. All configurations to the generator is configured through a YAML formatted file stored in the S3 artefact bucket. The deployment to AWS account is done by using AWS Cloud Development Kit (CDK)
1. AWS CDK generates the CloudFromation template and deploy it in the hosting AWS Account
2. Cloudfromation creates:

   1. The artefacts S3 Bucket and uploads the TDG PySpark library and YAML configuration file into it.

   2. The TDG PySpark glue Job

   3. The Service IAM role required by TDG PySpark glue Job.

3. The TDG PySpark glue Job is invoked to generate the test data.

## Deployment Options

You can deploy the AWS Glue Test Data Generator using either **AWS CDK** or **Terraform**.

### Option 1: AWS CDK Deployment

1. Clone the GitHub repository in your local development environment
2. Set the following environment variables:
   - `AWS_ACCOUNT` to the AWS account id where you intend to deploy the Test Data Generator
   - `AWS_REGION` to the AWS region id where you intend to deploy the Test Data Generator
3. Use aws configure to configure the AWS CLI with the access key to the AWS account
4. If the account is not CDK bootstrapped, you need to run the following command:
   ```bash
   cdk bootstrap
   ```
5. Open a terminal in the workspace path and run the following CDK command to deploy the solution:
   ```bash
   cd <workspace-path>/AWSGluePysparkTDG
   cdk deploy
   ```

### Option 2: Terraform Deployment ⭐ **Recommended**

#### Prerequisites
1. **Install Terraform** (>= 1.0):
   ```bash
   # Windows: Download from https://www.terraform.io/downloads.html
   # macOS: brew install terraform
   # Linux: sudo apt-get install terraform
   ```

2. **Configure AWS CLI**:
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, Region, and output format
   ```

#### Deploy with Terraform

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

2. **Configure variables (Optional)**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your preferred settings
   ```

3. **Plan the deployment**:
   ```bash
   terraform plan
   ```

4. **Apply the deployment**:
   ```bash
   terraform apply
   # Type 'yes' when prompted to confirm
   ```

5. **Verify deployment**:
   After successful deployment, you'll see outputs including:
   - S3 bucket name for artifacts
   - Glue job name and ARN
   - IAM role details
   - Configuration file path


## Configuration

### Configuration File

The Test Data Generator is configured through the YAML file `TDG_configuration_file.yml` found in the artefacts bucket at the following path:

`s3://tdg-artefacts-<account-id>/tgd_glue_job/Config/TDG_configuration_file.yml`

### Configuration Parameters

### **number_of_generated_records** 
Number of desired generated records 
### **attributes_list** 
Descriptor of the generated record fields/columns. You can configure the following data types:

* **Unique Key Generator**

> **ColumnName**: _Column name_

> **Generator**: **key_generator**

> **DataDescriptor**:
>       
>>  **Prefix**: _(optional) prefix to the key generated values_
>
>>  **LeadingZeros**: (_optional) number of digits formatting the key values. Key values are prefixed by leading zeros to generated a fixed number of digits_

   * **Child Key Generator**

> **ColumnName**: _Column name_

> **Generator**: **child_key_generator**

> **DataDescriptor**:
>      
>>  **Prefix**: _prefix should match the parent key prefix_
>
>>  **LeadingZeros**: _should match the parent key LeadingZero_
>
>>  **ChildCountPerSublevel**: a list of number of nodes per hierarchy sub-levels. For example, the following list describes three levels of hierarchy with level 1 has 10 nodes, level 2 has 100 nodes and level 3 has 1000 nodes. 
>
>>        - 10
>>        - 100
>>        - 1000
>

   * **String Data Generator**
>**1. Strings from a Dictionary**

> **ColumnName**: _Column name_

> **Generator**: **string_generator**

> **DataDescriptor**:
>     
>>  **Values**: _a list of string values._ 

>**2. Strings from a Pattern**

> **ColumnName**: _Column name_

> **Generator**: **string_generator**

> **DataDescriptor**:
>  
> > **Pattern**: _a pattern of expressions separated by #. available expressions:_ 
> > 1. Constant strings: can be any constant string such as: Contact Details, @, Title:, ..etc
> > 2. Random Numbers: ^N<length> for example to specify 8 digits: ^N8
> > 3. Random Alphabetic Strings: ^A<length> for example to specify a random string of length 10 charters: ^A10
> > 4. Random Alphanumeric Strings: ^x<length> for example to specify a random alphanumeric string of length 5 charters: ^X5

> > Example, the following pattern
>
> > **Contact Details: Email: #^X8#__#^N2#@#^A4#.#^A3# Phone: #^N8"**
>
> > will result in the following sample values:
>
> > Contact Details: Email: dTJeG0vO__65@rAeF.Dsh Phone: 9643728
>
> > Contact Details: Email: H8bmzlVP__8@KlVQ.Swc Phone: 84716259
>
> > Contact Details: Email: FAoNEfDV__6@HAYI.Jkp Phone: 4651938


>**3. Random Strings**

> **ColumnName**: _Column name_

> **Generator**: **string_generator**

> **DataDescriptor**:
>  
> >**Random: 'True'**
>
> >**NumChar**: _length of generated alphanumeric strings_

   * **Integer Data Generator** 

> **ColumnName**: _Column name_

> **Generator**: **integer_generator**

> **DataDescriptor**:
>  
> >**Range**: _lower value, upper value_

   * **Float/Double Data Generator** 

> **ColumnName**: _Column name_

> **Generator**: **float_generator**

> **DataDescriptor**:
>  
> > ** Expression**: _SQL expression such as: rand(42) * 3000_

   * **Date Data Generator**

> **ColumnName**: _Column name_

> **Generator**: **date_generator**

> **DataDescriptor**:
>  
> >**StartDate**: _start date of the date range on the format DD/MM/YYYY_ 
>
> >**EndDate**: _end date of the date range on the format DD/MM/YYYY_ 

   * **Close Date Data Generator**

> **ColumnName**: _Column name_

> **Generator**: **close_date_generator**

> **DataDescriptor**:
>  
> >**StartDateColumnName**: _column name of the generated open date_
>
> >**CloseDateRangeInDays**: _maximum span form the open date in days_

   * **Internet Address Data Generator**

> **ColumnName**: _Column name_

> **Generator**: **ip_address_generator**

> **DataDescriptor**:
>  
> >**IpRanges**: list of  ranges for the IP address four numeric parts on the form of _lower value, upper value_. For example:
>
>>      - 9,10
>>      - 1,254
>>      - 1,128
>>      - 2,20
>

### target_list
the list of targets for the generator. The generator will perform automatic data types conversion for every specified target. Currently, the generator supports the following targets:

* S3 Buckets
>
>  **target**: **S3**
>
>    **attributes**:
>
>>**BucketArn**: _S3 Bucket arn including the prefix_
>
>>**mode**: _s3 bucket writing mode (overwrite, append)_ 
>
>>**header**: _include header in the generated data (True, Flase)_
>
>>**delimiter**: _CSV file delimeter_

* DynamoDB tables 
>
>  **target**: **Dynamodb**
>
>    **attributes**:
>
>>**dynamodb.output.tableName**: _dynamodb table name_
>
>>**dynamodb.throughput.write.percent**: _throughput write percent_

## Invocation
From the AWS Glue Console:
1. Navigate to **Data Integration and ETL>AWS Glue Studio]>Jobs**
2. Select the **TestDataGeneratorJob **job and press** Run Job**
3. Once the job completes successfully, check for the generated data in the configured targets.



## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


## Contributors

* [Mohamed Elbishbeashy](https://www.linkedin.com/in/mbishbeashy/) - Wrote the initial version.
