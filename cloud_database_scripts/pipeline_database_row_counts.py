import mysql.connector
from mysql.connector import Error

def pipeline_database_row_counts(host, database, user, password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():

            db_info = connection.server_info
            print(f"Connected to MySQL Server version {db_info}\n")

            cursor = connection.cursor()

            query = f"SELECT COUNT(*) FROM image"
            cursor.execute(query)
            # fetchone() returns a tuple, we access the first element (index 0)
            row_count = cursor.fetchone()[0]
            print(f"The table 'image' has {row_count} rows.")

            query = f"SELECT COUNT(*) FROM image_event"
            cursor.execute(query)
            # fetchone() returns a tuple, we access the first element (index 0)
            row_count = cursor.fetchone()[0]
            print(f"The table 'image_event' has {row_count} rows.")

            query = f"SELECT COUNT(*) FROM image_event_alert"
            cursor.execute(query)
            # fetchone() returns a tuple, we access the first element (index 0)
            row_count = cursor.fetchone()[0]
            print(f"The table 'image_event_alert' has {row_count} rows.")
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

    pipeline_database_row_counts(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
