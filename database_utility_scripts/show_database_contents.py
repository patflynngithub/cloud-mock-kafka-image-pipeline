import mysql.connector
from mysql.connector import Error

def show_database_contents(host, database, user, password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host     = host,
            database = database,
            user     = user,
            password = password
        )

        if connection.is_connected():

            db_info = connection.server_info
            print(f"Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()

            print(f"Showing {database} database table contents\n")

            table_names = ['image', 'image_event', 'image_event_alert']
            for table_name in table_names:
                select_query = f"SELECT * FROM {table_name}"
                cursor.execute(select_query)
                result = cursor.fetchall()

                print(f"\nContents of table '{table_name}':")
                for row in result:
                    print(row)
            print()

            connection.commit()

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
    DB_NAME     = "image_pipeline"
    DB_USER     = "admin"
    DB_PASSWORD = "nancygraceroman"

    show_database_contents(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

