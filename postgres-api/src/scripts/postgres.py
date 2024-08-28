import psycopg2

class Postgres:

    def __init__(self, database, user, password, host, port):

        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        
    
    def execute_query(self, query_str):

        cursor = self.connection.cursor()
        cursor.execute(query_str)
        record = self.cursor.fetchall()
        cursor.close()

        return record