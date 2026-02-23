"""
This database utility counts the number of rows of data in each image pipeline
database table.

Execution:
    $ python3 database_utility_scripts/pipeline_database_row_counts.py
    or
    $ cd database_utility_scripts
    $ python3 pipeline_database_row_counts.py
"""

import mysql.connector
from mysql.connector import Error

import sys

# Allows this utility to access the main application's CLOUD_INFO
# module when the utility is executed from one of two places: 
# 1) the main application directory, or
# 2) the subdirectory that the utility is in
sys.path.append("./CLOUD_INFO")   # add to module search path
sys.path.append("../CLOUD_INFO")  # add to module search path

# RDS endpoint and database credentials
from CLOUD_INFO import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# =====================================================================

def pipeline_database_row_counts(host, database, user, password):
    """
    Displays number of data rows in each database table.
    """

    rdb_connection = None
    try:
        rdb_connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if rdb_connection.is_connected():

            rdb_info = rdb_connection.server_info
            print(f"Connected to MySQL Server version {rdb_info}\n")

            cursor = rdb_connection.cursor()

            table_names = ["image_metadata", "image_event", "image_event_alert"]
            for table_name in table_names:
                query = f"SELECT COUNT(*) FROM {table_name}"
                cursor.execute(query)
                # fetchone() returns a tuple, we access the first element (index 0)
                row_count = cursor.fetchone()[0]
                print(f"The table '{table_name}' has {row_count} rows.")

            print()

            rdb_connection.commit()

    except Error as e:
        print(f"Error connecting to MySQL database: {e}")

    finally:
        if rdb_connection is not None and rdb_connection.is_connected():
            cursor.close()
            rdb_connection.close()
            print("MySQL connection is closed.")

# -------------------------------------------------------------------

if __name__ == "__main__":

    pipeline_database_row_counts(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

