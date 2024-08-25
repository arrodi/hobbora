import psycopg2
from os import environ

connection = psycopg2.connect(database=environ["POSTGRES_DB"], user=environ["POSTGRES_USER"], password=environ["POSTGRES_PASSWORD"], host=environ["POSTGRES_HOST"], port=environ["POSTGRES_PORT"])

cursor = connection.cursor()

sql_context ="""
select 
    *
from 
    customers
"""

cursor.execute(sql_context)

# Fetch all rows from database TEST
record = cursor.fetchall()

print("Data from Database:- ", record)