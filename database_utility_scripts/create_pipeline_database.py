"""
This database utility creates the relational database for the mock image pipeline.
It can also be used when the database already exists; in this case, it will only
drop the tables (THEREBY DELETING ALL DATA IN THE TABLES) and recreate them empty.

Execution:
    $ python3 database_utility_scripts/create_pipeline_database.py
    or
    $ cd database_utility_scripts
    $ python3 create_pipeline_database.py
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
from CLOUD_INFO import DB_HOST, DB_USER, DB_PASSWORD

# =====================================================================

def create_pipeline_database(host, user, password):
    """
    Creates the image pipeline database if it doesn't yet exist and
    creates its table (dropping and recreating them if they already exist).
    """

    rdb_connection = None
    cursor         = None
    try:
        rdb_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if rdb_connection.is_connected():

            rdb_info = rdb_connection.server_info
            cursor   = rdb_connection.cursor()
            print(f"Connected to MySQL Server version {rdb_info}")

            # Create database itself if it doesn't already exist
            database_name = "image_pipeline"
            print(f"Creating {database_name} database if it does not exist")
            create_database = f"CREATE DATABASE IF NOT EXISTS {database_name}"
            cursor.execute(create_database)

            # Show existing databases associated with this EC2 instance
            print("\nDatabases associated with this EC2 instance:")
            cursor.execute("SHOW DATABASES")
            for db in cursor:
                print(db)

            # use image_pipeline database
            cursor.execute(f"USE {database_name}")

            print()

            # disables foreign key checks so can drop tables
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # Create image metadata table (anew if already exists)
            table_name = "image_metadata"
            drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
            cursor.execute(drop_table_query) 
            create_table_query = f"""
              CREATE TABLE {table_name} (
              image_id          INT AUTO_INCREMENT PRIMARY KEY,
              image_filename    VARCHAR(255) NOT NULL UNIQUE,
              image_object_key  VARCHAR(255) UNIQUE
            );
            """
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully")

            # Create image event table (anew if already exists)
            foreign_key_table_name = table_name
            table_name = "image_event"
            drop_table_query = f"DROP TABLE IF EXISTS {table_name}"                 
            cursor.execute(drop_table_query)
            create_table_query = f"""
              CREATE TABLE {table_name} (
              image_event_id              INT AUTO_INCREMENT PRIMARY KEY,
              image_id                    INT NOT NULL,
              difference_image_object_key VARCHAR(255),
              FOREIGN KEY (image_id) REFERENCES {foreign_key_table_name}(image_id)
            );
            """
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully")

            # Create image event alert table (anew if already exists)
            foreign_key_table_name = table_name
            table_name = "image_event_alert"
            drop_table_query = f"DROP TABLE IF EXISTS {table_name}"                 
            cursor.execute(drop_table_query)
            create_table_query = f"""
              CREATE TABLE IF NOT EXISTS {table_name} (
              image_event_alert_id  INT AUTO_INCREMENT PRIMARY KEY,
              image_event_id        INT NOT NULL UNIQUE,
              FOREIGN KEY (image_event_id) REFERENCES {foreign_key_table_name}(image_event_id)
            );
            """
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully")

            rdb_connection.commit()

            # Show database's tables
            query = "SHOW TABLES"
            cursor.execute(query)
            tables = cursor.fetchall()
            if tables:
                print("\nCREATE statements for tables in the database:")
                for table in tables:
                    # 'SHOW TABLES' returns a tuple for each table, 
                    # the name is the first element
                    table_name = table[0]

                    # Show the CREATE TABLE query that created the table
                    query = f"SHOW CREATE TABLE {table_name}"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result:
                        # The 'Create Table' statement is in the second column (index 1) of the result
                        print(f"\nTable: '{table_name}':")
                        print(   "-------" + '-'*(len(table_name)+2))
                        print(result[1])
                    else:
                        print(f"\tTable '{table_name}' not found or no schema information available.")

                    """
                    # Show the table's schema info that is provided by the DESCRIBE TABLE query
                    query = f"DESCRIBE {table_name}"
                    cursor.execute(query)
                    schema_info = cursor.fetchall()
                    print(f"\tSchema for table '{table_name}':")
                    for column in schema_info:
                        # The 'column' tuple typically contains (Field, Type, Null, Key, Default, Extra)
                        print(f"\t\t* Field: {column[0]}, Type: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}, Extra: {column[5]}")
                        # print(f"\t\t{column}")
                    """
            else:
                print("No tables found in the database.")
            print()

    except Error as e:
        print(f"Error connecting to MySQL database: {e}")

    finally:
        if rdb_connection is not None and rdb_connection.is_connected():
            cursor.close()
            rdb_connection.close()
            print("MySQL connection is closed.")

# -------------------------------------------------------------------

if __name__ == "__main__":

    create_pipeline_database(DB_HOST, DB_USER, DB_PASSWORD)

