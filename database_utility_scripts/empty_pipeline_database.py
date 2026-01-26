import mysql.connector
from mysql.connector import Error

def empty_pipeline_database(host, database, user, password):
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
            print(f"Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            print("Foreign key checks are temporarily disabled for truncating tables")

            print(f"Emptying the {database} database ...")
            cursor.execute("USE image_pipeline")
            cursor.execute("TRUNCATE TABLE image")
            cursor.execute("TRUNCATE TABLE image_event")
            cursor.execute("TRUNCATE TABLE image_event_alert")

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

    empty_pipeline_database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
