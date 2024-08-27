import psycopg2

class Postgres:

    def __init__(self, database, user, password, host, port):

        connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = connection.cursor()
    
    def execute_query(self, query_str):

        self.cursor.execute(query_str)

        # Fetch all rows from database TEST
        record = self.cursor.fetchall()

        return record