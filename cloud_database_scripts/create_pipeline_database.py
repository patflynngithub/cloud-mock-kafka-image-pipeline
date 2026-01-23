import mysql.connector
from mysql.connector import Error

def create_pipeline_database(host, user, password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if connection.is_connected():

            db_info = connection.server_info
            print(f"Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()

            print("Creating image_pipeline database if it does not exist")
            create_database = "CREATE DATABASE IF NOT EXISTS image_pipeline"
            cursor.execute(create_database)

            print("\nDatabases on the server:")
            cursor.execute("SHOW DATABASES")
            for db in cursor:
                print(db)

            cursor.execute("USE image_pipeline")

            print()

            # Create image table
            create_table_query = """
              CREATE TABLE IF NOT EXISTS image (
              image_id  INT AUTO_INCREMENT PRIMARY KEY,
              filename  VARCHAR(255) NOT NULL UNIQUE,
              image_key VARCHAR(255) UNIQUE
            );
            """
            cursor.execute(create_table_query)
            print("Table 'image' created successfully or already exists.")

            # Create image_event table
            create_table_query = """
              CREATE TABLE IF NOT EXISTS image_event (
              image_event_id       INT AUTO_INCREMENT PRIMARY KEY,
              image_id             INT NOT NULL,
              difference_image_key VARCHAR(255),
              FOREIGN KEY (image_id) REFERENCES image(image_id)
            );
            """
            cursor.execute(create_table_query)
            print("Table 'image_event' created successfully or already exists.")

            # Create image_event_alert table
            create_table_query = """
              CREATE TABLE IF NOT EXISTS image_event_alert (
              image_event_alert_id  INT AUTO_INCREMENT PRIMARY KEY,
              image_event_id        INT NOT NULL UNIQUE,
              FOREIGN KEY (image_event_id) REFERENCES image_event(image_event_id)
            );
            """
            cursor.execute(create_table_query)
            print("Table 'image_event_alert' created successfully or already exists.")

            connection.commit()

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
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":

    # RDS endpoint and database credentials
    DB_HOST     = "image-pipeline.cja6aao2uw8s.us-west-2.rds.amazonaws.com"
    DB_USER     = "admin"
    DB_PASSWORD = "nancygraceroman"

    create_pipeline_database(DB_HOST, DB_USER, DB_PASSWORD)
