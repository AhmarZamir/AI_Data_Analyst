import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection


def execute_query(query):

    connection = get_connection()

    try:

        with connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    "SET TRANSACTION READ ONLY"
                )

                cursor.execute(query)

                return cursor.fetchall()

    finally:

        connection.close()
