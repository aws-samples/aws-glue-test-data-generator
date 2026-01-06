import sys
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    MapType,
    StringType,
    StructType,
    StructField,
    IntegerType,
    FloatType,
)
from pyspark.sql.functions import (
    lit,
    col,
    rand,
    slice,
    shuffle,
    concat_ws,
    split,
    lpad,
    expr,
    to_date,
    date_add,
)
import string
from datetime import datetime


# Transformation Library
tmp_id_global_counter = 0
generated_keys_list = []


def helper_recursive_key_generator(
    level, parent, sublevel_children_number_list, number_of_generated_records
):
    """
    Helper function for TestDataGeneratorLib.child_key_generator method.
    It recursively generates child keys for a given number of records.
    Args:
        level (int): The current level in the hierarchy.
        parent (int): The parent id.
        sublevel_children_number_list (list): The number of children per level.
        number_of_generated_records (int): The total number of records to generate.
    """
    global tmp_id_global_counter, generated_keys_list
    for subcompcountforsublevel in range(sublevel_children_number_list[level]):
        if tmp_id_global_counter < number_of_generated_records:
            if level != 0:
                generated_keys_list.append(
                    {"CHILD_KEY": tmp_id_global_counter, "PARENT_KEY": parent}
                )
            tmp_id_global_counter += 1
            if level < len(sublevel_children_number_list) - 1:
                helper_recursive_key_generator(
                    level + 1,
                    tmp_id_global_counter,
                    sublevel_children_number_list,
                    number_of_generated_records,
                )


class DataGeneratorLib:
    """
    A library of methods for generating test data for use in unit tests and other development tasks.
    """

    def __init__(self, spark: SparkSession, number_of_generated_records) -> None:
        """
        Initializes the TestDataGeneratorLib instance with the specified SparkSession and the number of generated records.
        Args:
            spark (SparkSession): The SparkSession instance.
            number_of_generated_records (int): The number of generated records.
        """
        self.spark = spark
        self.number_of_generated_records = number_of_generated_records
        self.random_seed = 52

    def string_generator(self, df, descriptor, column_name):
        """
        Generates a column of strings based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "Values" in descriptor:
            lookup_data = [
                {"SG_LK_id": descriptor["Values"].index(value), f"{column_name}": value}
                for value in descriptor["Values"]
            ]
            lookup_df = self.spark.createDataFrame(lookup_data)
            df = df.withColumn(
                "tempid", rand(seed=self.random_seed) * (len(descriptor["Values"]))
            )
            df = df.withColumn("tempid", col("tempid").cast(IntegerType()))
            df = (
                df.join(lookup_df, df.tempid == lookup_df.SG_LK_id, "outer")
                .drop(col("tempid"))
                .drop(col("SG_LK_id"))
            )
        elif "Random" in descriptor and descriptor["Random"] == "True":
            source_characters = string.ascii_letters + string.digits
            df = df.withColumn(
                "SG_source_characters", split(lit(source_characters), "")
            )
            df = df.withColumn(
                f"{column_name}",
                concat_ws(
                    "",
                    slice(
                        shuffle(col("SG_source_characters")), 1, descriptor["NumChar"]
                    ),
                ),
            )
            df = df.drop(col("SG_source_characters"))
        elif "Pattern" in descriptor:
            x_characters = string.ascii_letters + string.digits
            n_characters = string.digits
            a_characters = string.ascii_letters
            df = df.withColumn("x_characters", split(lit(x_characters), ""))
            df = df.withColumn("n_characters", split(lit(n_characters), ""))
            df = df.withColumn("a_characters", split(lit(a_characters), ""))
            token_list = descriptor["Pattern"].split("#")
            df = df.withColumn(f"{column_name}", lit(None))
            for token in token_list:
                if token.startswith("^X"):
                    string_length = int(token[2:])
                    df = df.withColumn(
                        f"{column_name}",
                        concat_ws(
                            "",
                            col(f"{column_name}"),
                            slice(shuffle(col("x_characters")), 1, string_length),
                        ),
                    )
                elif token.startswith("^N"):
                    string_length = int(token[2:])
                    df = df.withColumn(
                        f"{column_name}",
                        concat_ws(
                            "",
                            col(f"{column_name}"),
                            slice(shuffle(col("n_characters")), 1, string_length),
                        ),
                    )
                elif token.startswith("^A"):
                    string_length = int(token[2:])
                    df = df.withColumn(
                        f"{column_name}",
                        concat_ws(
                            "",
                            col(f"{column_name}"),
                            slice(shuffle(col("a_characters")), 1, string_length),
                        ),
                    )
                else:
                    df = df.withColumn(
                        f"{column_name}",
                        concat_ws("", col(f"{column_name}"), lit(token)),
                    )
            df = df.drop(col("x_characters"))
            df = df.drop(col("n_characters"))
            df = df.drop(col("a_characters"))
        return df

    def key_generator(self, df, descriptor, column_name):
        """
        Generates a column of string unique keys based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "Prefix" in descriptor:
            df = df.withColumn(
                f"{column_name}",
                concat_ws(
                    "",
                    lit(descriptor["Prefix"]),
                    lpad(col("id"), descriptor["LeadingZeros"], "0"),
                ),
            )
        else:
            df = df.withColumn(
                f"{column_name}", lpad(col("id"), descriptor["LeadingZeros"], "0")
            )
        return df

    def child_key_generator(self, df, descriptor, column_name):
        """
        Generates a column of string child hierarchical keys based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        global tmp_id_global_counter, generated_keys_list
        tmp_id_global_counter = 0
        generated_keys_list = []
        helper_recursive_key_generator(
            0, 0, descriptor["ChildCountPerSublevel"], self.number_of_generated_records
        )
        child_list_data = generated_keys_list
        child_list_df = self.spark.createDataFrame(child_list_data)
        if "Prefix" in descriptor:
            child_list_df = child_list_df.withColumn(
                "PARENT_KEY",
                concat_ws(
                    "",
                    lit(descriptor["Prefix"]),
                    lpad(col("PARENT_KEY"), descriptor["LeadingZeros"], "0"),
                ),
            )
        else:
            child_list_df = df.withColumn(
                "PARENT_KEY", lpad(col("PARENT_KEY"), descriptor["LeadingZeros"], "0")
            )
        child_list_df = child_list_df.withColumnRenamed("PARENT_KEY", f"{column_name}")

        # child_list_df.printSchema()
        child_list_df.show()
        df = df.join(child_list_df, df.id == child_list_df.CHILD_KEY, "outer").drop(
            col("CHILD_KEY")
        )
        return df

    def float_generator(self, df, descriptor, column_name):
        """
        Generates a column of float values based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "Expression" in descriptor:
            df = df.withColumn(f"{column_name}", expr(descriptor["Expression"]))
            df = df.withColumn(
                f"{column_name}", col(f"{column_name}").cast(FloatType())
            )
        return df

    def date_generator(self, df, descriptor, column_name):
        """
        Generates a column of dates based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "StartDate" in descriptor:
            df = df.withColumn(
                f"{column_name}", to_date(lit(descriptor["StartDate"]), "dd/MM/yyyy")
            )
            if "EndDate" in descriptor:
                start_date_object = datetime.strptime(
                    descriptor["StartDate"], "%d/%m/%Y"
                )
                end_date_object = datetime.strptime(descriptor["EndDate"], "%d/%m/%Y")
                delta_days = end_date_object - start_date_object
                df = df.withColumn(
                    "tempid", rand(seed=self.random_seed) * delta_days.days
                )
                df = df.withColumn("tempid", col("tempid").cast(IntegerType()))
                df = df.withColumn(
                    f"{column_name}", expr(f"date_add({column_name}, tempid)")
                ).drop("tempid")
            if "CastString" in descriptor and descriptor["CastString"] == "y":
                df = df.withColumn(
                    f"{column_name}", col(f"{column_name}").cast(StringType())
                )
        return df

    def close_date_generator(self, df, descriptor, column_name):
        """
        Generates a column of close dates based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "StartDateColumnName" in descriptor and "CloseDateRangeInDays" in descriptor:
            delta_days = int(descriptor["CloseDateRangeInDays"])
            df = df.withColumn("tempid", rand(seed=self.random_seed) * delta_days)
            df = df.withColumn("tempid", col("tempid").cast(IntegerType()))
            df = df.withColumn(
                f"{column_name}",
                expr(f"date_add({descriptor['StartDateColumnName']}, tempid)"),
            ).drop("tempid")
            if "CastString" in descriptor and descriptor["CastString"] == "y":
                df = df.withColumn(
                    f"{column_name}", col(f"{column_name}").cast(StringType())
                )
        return df

    def integer_generator(self, df, descriptor, column_name):
        """
        Generates a column of integers based on the given descriptor.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        if "Seed" in descriptor:
            seed = int(descriptor["Seed"])
        else:
            seed = self.random_seed

        if "Range" in descriptor:
            token_list = descriptor["Range"].split(",")
            lower_limit = int(token_list[0])
            upper_limit = int(token_list[1]) + 1
            df = df.withColumn(
                column_name,
                lower_limit + (rand(seed=seed) * (upper_limit - lower_limit)),
            )
            df = df.withColumn(column_name, col(column_name).cast(IntegerType()))
        return df

    def ip_address_generator(self, df, descriptor, column_name):
        """
        Generates a column of strings with random internet IP address.
        Args:
            df (DataFrame): The DataFrame to which the generated column will be added.
            descriptor (dict): A dictionary containing the parameters for generating the column.
            column_name (str): The name of the column to be generated.
        Returns:
            DataFrame: The input DataFrame with the new column added.
        """
        tmp_discriptor = {}
        df = df.withColumn(f"{column_name}", lit(None))
        for i in range(1, 5):
            if "IpRanges" in descriptor and len(descriptor["IpRanges"]) >= i:
                tmp_discriptor["Range"] = descriptor["IpRanges"][i - 1]
            else:
                tmp_discriptor["Range"] = "1,254"

            tmp_discriptor["Seed"] = i
            df = self.integer_generator(df, tmp_discriptor, "temp_ip_gen_col")
            separtor = "" if i == 1 else "."
            df = df.withColumn(
                f"{column_name}",
                concat_ws(separtor, col(f"{column_name}"), col("temp_ip_gen_col")),
            )
            df = df.drop(col("temp_ip_gen_col"))
        return df
