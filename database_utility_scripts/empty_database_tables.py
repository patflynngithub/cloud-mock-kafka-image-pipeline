"""
This database utility truncates (empties) the relational database tables for the
mock image pipeline.

Execution:
    $ python3 database_utility_scripts/empty_database_tables.py
    or
    $ cd database_utility_scripts
    $ python3 empty_database_tables.py
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

def empty_database_tables(host, database, user, password):
    """
    Empties the image pipeline's database tables.
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
            print(f"Connected to MySQL Server version {rdb_info}")

            cursor = rdb_connection.cursor()

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            print("Foreign key checks are temporarily disabled for truncating tables")

            print(f"Emptying the '{database}' database tables ...")
            cursor.execute(f"USE {database}")

            table_names = ["image_metadata", "image_event", "image_event_alert"]
            for table_name in table_names:
                print(f"Emptying table '{table_name}'")
                cursor.execute(f"TRUNCATE TABLE {table_name}")

            rdb_connection.commit()

    except Error as e:
        print(f"Error connecting to MySQL database: {e}")

    finally:
        if rdb_connection is not None and rdb_connection.is_connected():
            cursor.close()
            rdb_connection.close()
            print("MySQL connection is closed.")

# --------------------------------------------------------------------------

if __name__ == "__main__":

    empty_database_tables(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

