## AWS Glue Test Data Generator
The AWS Glue Test Data Generator provides a configurable framework for Relational Test Data Generation using AWS Glue Pyspark Jobs. The required test data description is fully configurable through a YAML configuration file. 

The Test Data Generation Framework currently supports the following types:

* Unique Key Generator

  This generator produces formatted unique values that can be used as partition key. you can specify a prefix to and the number of leading zeros if required.

* Child Key Generator

  This generator produces a child key referencing the primary key. This is useful in generating multi-level hierarchical data. you can specify the number of levels and how many nodes you want to generate per level.

* String Data Generator 

  This generator produces String data type with various mechanisms:

   * Random Strings: you can specify the number of characters and the type of generated characters: numeric, alphabetic or alphanumeric values. This can be used for generating random serial numbers, ordinal data, codes, identity numbers, .. etc.

  * Strings from a Dictionary: you can provide a dictionary of words to pick up randomly by the generator. This can be used to generate categorical columns with predefined set of values such as order status, product types, marital status, gender,..etc/

  * Strings from a Pattern: you can provide generic pattern for your string data. This can be used to generate fake emails, formatted phone numbers, comments, address like data, …etc.

* Float/Double Data Generator 

  This generator produces random float/double data from an expression. This can be used to generate float values such as salary, temperature, profit, statistical data,.. etc

* Date Data Generator

  This generator produces random dates generator from a configurable date range.

* Close Date Data Generator

  This generator produces random from a configurable start date column and a range. This can be used to generate dates of specific intervals such as a support ticket close date, deceased date, expiration date,… etc


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

