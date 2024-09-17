class Queries:

    def __init__(self):
        self.table_schemas = {
            "USER_ACCOUNTS": {
                "USER_EMAIL": "text PRIMARY KEY",
                "USER_NAME": "text",
                "USER_PASS": "text",
                "USER_RATING": "decimal",
                "USER_SCHOOL": "text",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            "USER_HOBBIES" : {
                        "USER_EMAIL": "text REFERENCES USER_ACCOUNTS (USER_EMAIL)",
                        "HOBBY_NAME": "text PRIMARY KEY",
                        "HOBBY_DESCRIPTION": "text",
                        "HOBBY_PROFICIENCY": "text",
                        "EXPERIENCE_YEARS": "integer",
                        "EXPERIENCE_MONTHS": "integer",
                        "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                        "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    }
        }

    def create_table(self, table_nm, table_columns):
        
        data_lst = []
        for _column_nm, _column_config in table_columns.items():
             data_lst.append(f"{_column_nm} {_column_config}")

        data_str = ", ".join(data_lst)

        sql = f"""
                CREATE TABLE IF NOT EXISTS {table_nm}
                    ({data_str})
                """
        
        return sql
    
    def insert_into_table(self, table_nm, table_data):
        
        column_lst = []
        value_lst = []
        for _column_nm, _column_value in table_data.items():
             column_lst.append(_column_nm)
             value_lst.append(f"'{_column_value}'")

        column_str = ", ".join(column_lst)
        value_str = ", ".join(value_lst)

        sql_context =f"""
        INSERT INTO
            {table_nm} ({column_str})
            VALUES ({value_str});
        """
        
        return sql_context
    
    def select_table(self, table_nm, table_columns_lst, where_clause):
        table_columns_str = ", ".join(table_columns_lst)
        sql_context =f"""
            SELECT 
                {table_columns_str}
            FROM 
                {table_nm}
            WHERE
                {where_clause}
            """
        
        return sql_context
        
    def table_function(self, function_nm):
    
        sql = f"""
                CREATE OR REPLACE FUNCTION {function_nm}()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.UPD_DT = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                """
        return sql
    
    def function_trigger(self, table_nm, function_nm):
        sql = f"""
        CREATE TRIGGER {table_nm}_TRIGGER_{function_nm}
        BEFORE UPDATE ON {table_nm}
        FOR EACH ROW
        EXECUTE FUNCTION {function_nm}();
        """

        return sql
    
    def drop_tables(self):
        sql = """
        DO $$ 
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        """

        return sql