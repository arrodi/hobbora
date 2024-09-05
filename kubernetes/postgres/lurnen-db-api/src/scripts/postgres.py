import psycopg2

class Postgres:

    def __init__(self, database, user, password, host, port):

        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        dummy_val = self.test_connection()
        self.create_user_account_table()
    
    def execute_query(self, query_str, return_bool=False):

        cursor = self.connection.cursor()
        cursor.execute(query_str)
        cursor.connection.commit()
        if return_bool:
            record = cursor.fetchall()
        else:
            record = []
        cursor.close()

        return record
    
    def test_connection(self):
        print("CONNECTING TO POSTGRESQL")
        cursor = self.connection.cursor()
        test_sql =  """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public';
                    """
        cursor.execute(test_sql)
        record = cursor.fetchall()
        print("CONNECTION SUCCESFUL")
        if record:
            print("TABLES AVAILABLE:")
            for _item in record[0]:
                print(_item)
        else:
            print("NO TABLES AVAILABLE")
        cursor.close()

        return record
    
    def create_user_account_table(self):
        print("CREATING USER_ACCOUNT TABLE")
        cursor = self.connection.cursor()
        test_sql =  """
                    CREATE TABLE IF NOT EXISTS USER_ACCOUNTS
                        (USER_EMAIL text PRIMARY KEY, USER_NAME text, USER_PASS text);
                    """
        cursor.execute(test_sql)
        
        if cursor.connection.notices:
            print(cursor.connection.notices[-1])
        
        self.connection.commit()
        cursor.close()