"""
This database utility shows the contents of the database tables.

Execution:
    $ python3 database_utility_scripts/show_database_contents.py
    or
    $ cd database_utility_scripts
    $ python3 show_database_contents.py
"""

import sys

import mysql.connector
from mysql.connector import Error

# Allows this utility to access the main application's CLOUD_INFO
# module when the utility is executed from one of two places: 
# 1) the main application directory, or
# 2) the subdirectory that the utility is in
sys.path.append("./CLOUD_INFO")   # add to module search path
sys.path.append("../CLOUD_INFO")  # add to module search path

# RDS endpoint and database credentials
from CLOUD_INFO import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# =====================================================================

def show_database_contents(host, database, user, password):
    """
    Shows the contents of the database tables.    
    """

    rdb_connection = None
    try:
        rdb_connection = mysql.connector.connect(
            host     = host,
            database = database,
            user     = user,
            password = password
        )

        if rdb_connection.is_connected():

            rdb_info = rdb_connection.server_info
            print(f"Connected to MySQL Server version {rdb_info}")

            cursor = rdb_connection.cursor()

            print(f"Showing '{database}' database table contents\n")

            table_names = ['image_metadata', 'image_event', 'image_event_alert']
            for table_name in table_names:
                select_query = f"SELECT * FROM {table_name}"
                cursor.execute(select_query)
                result = cursor.fetchall()

                print(f"\nContents of table '{table_name}':")
                for row in result:
                    print(row)
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

    show_database_contents(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

