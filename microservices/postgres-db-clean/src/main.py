# AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.postgres import Postgres
from scripts.queries import Queries

settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)
queries = Queries()


def delete_db_object(table_nm, column_nm_lst, where_clause_str):
    sql_str = queries.select_table(table_nm, column_nm_lst, where_clause_str)
    result = postgres.execute_query(sql_str, True)
    delete_list = [item[0] for item in result]

    for _name in delete_list:
        if 'tables' in table_nm:
            sql_str = f"DROP TABLE IF EXISTS {_name} CASCADE;"
            postgres.execute_query(sql_str, True)
        if 'routines' in table_nm:
            sql_str = f"DROP FUNCTION IF EXISTS {_name}() CASCADE;"
            postgres.execute_query(sql_str, True)
        
    



delete_db_object(   "information_schema.tables",
                    ["table_name"],
                    "table_schema = 'public' AND table_type = 'BASE TABLE'")

delete_db_object(   "information_schema.routines",
                    ["routine_name"],
                    "routine_schema = 'public' AND routine_type  = 'FUNCTION'")