def create_table(table_nm, table_columns):
    
    data_lst = []
    for _column_nm, _column_config in table_columns.items():
            data_lst.append(f"{_column_nm} {_column_config}")

    data_str = ", ".join(data_lst)

    sql_query = f"""
            CREATE TABLE IF NOT EXISTS {table_nm}
            ({data_str})
            """
    
    return sql_query

def modify_record(table_nm, table_data, record_condition):

    column_lst = []
    value_lst = []
    for _column_nm, _column_value in table_data.items():
        column_lst.append(f"{_column_nm} = %s")
        value_lst.append(_column_value)

    record_data_str = ", ".join(column_lst)

    sql_query = f"""
            UPDATE {table_nm}
            SET {record_data_str}
            WHERE {record_condition};
            """
    
    return sql_query, value_lst

def delete_record(table_nm, record_condition):

    value_lst = []

    sql_query = f"""
            DELETE FROM {table_nm}
            WHERE {record_condition};
            """
    
    return sql_query, value_lst

def insert_into_table(table_nm, table_data):
    
    column_lst = []
    value_lst = []
    for _column_nm, _column_value in table_data.items():
            column_lst.append(_column_nm)
            value_lst.append(_column_value)

    column_str = ", ".join(column_lst)
    value_str = ", ".join(['%s'] * len(value_lst))

    sql_query =f"""
    INSERT INTO {table_nm}
    ({column_str})
    VALUES ({value_str});
    """
    
    return sql_query, value_lst

def select_table(table_nm, table_columns_lst, where_clause):
    table_columns_str = ", ".join(table_columns_lst)
    sql_context =f"""
        SELECT {table_columns_str}
        FROM {table_nm}
        WHERE {where_clause}
        """
    
    return sql_context

def select_join_table(table_nm_1, table_nm_2, table_columns_lst, join_column, where_clause = ""):
    table_columns_str = ", ".join(table_columns_lst)

    join_clause = f"a.{join_column} = b.{join_column}"

    if where_clause:
        sql_context =f"""
        SELECT {table_columns_str}
        FROM {table_nm_1} a
        INNER JOIN {table_nm_2} b
        ON {join_clause}
        WHERE {where_clause}
        """
    else:
        sql_context =f"""
        SELECT {table_columns_str}
        FROM {table_nm_1} a
        INNER JOIN {table_nm_2} b
        ON {join_clause}
        """
    
    return sql_context
    
def upd_dt_function(function_nm):

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

def tutoring_mode_function(function_nm):

    sql = f"""
            CREATE OR REPLACE FUNCTION {function_nm}()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.MODE_LIVE_CALL IS NULL THEN
                    NEW.MODE_LIVE_CALL := false;
                END IF;
                IF NEW.MODE_PUBLIC_IN_PERSON IS NULL THEN
                    NEW.MODE_PUBLIC_IN_PERSON := false;
                END IF;
                IF NEW.MODE_PRIVATE_IN_PERSON IS NULL THEN
                    NEW.MODE_PRIVATE_IN_PERSON := false;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
    return sql

def upd_dt_function_trigger(table_nm, function_nm):
    sql = f"""
    CREATE TRIGGER {table_nm}_TRIGGER_{function_nm}
    BEFORE UPDATE ON {table_nm}
    FOR EACH ROW
    EXECUTE FUNCTION {function_nm}();
    """

    return sql

def tutoring_mode_function_trigger(table_nm, function_nm):
    sql = f"""
    CREATE TRIGGER {table_nm}_TRIGGER_{function_nm}
    BEFORE INSERT ON {table_nm}
    FOR EACH ROW EXECUTE FUNCTION {function_nm}();
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