import psycopg2
import psycopg2.errorcodes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Postgres:
    def __init__(self, database, user, password, host, port):
        logger.info('Connecting to PostgreSQL database')
        logger.info(f'Database: {database} User: {user} Host: {host} Port: {port}')
        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    ################################################################################
    def prepare_db(self, queries, schemas):
        function_nm = "OVERWRITE_UPD_TS_ON_INSERT"
        function_sql_str = queries.upd_dt_function(function_nm)
        self.execute_query(function_sql_str)
        for table_name, column_name in schemas.table_schemas.items():
            create_sql_str = queries.create_table(table_name, column_name)
            self.execute_query(create_sql_str)
            if "UPD_DT" in column_name:
                trigger_sql_str = queries.upd_dt_function_trigger(table_name, function_nm)
                self.execute_query(trigger_sql_str)

        function_nm = "DEFAULT_TUTOR_MODE_ON_INSERT"
        function_sql_str = queries.tutoring_mode_function(function_nm)
        self.execute_query(function_sql_str)
        for table_name in ["USER_HOBBIES_TUTORING"]:
            trigger_sql_str = queries.tutoring_mode_function_trigger(table_name, function_nm)
            self.execute_query(trigger_sql_str)
    ################################################################################

    def execute_query(self, sql_query, sql_values='', fetch=False):
        try:
            with self.connection.cursor() as cursor:
                logger.info('EXECUTING:' + sql_query)
                
                if sql_values:
                    cursor.execute(sql_query, sql_values)
                else:
                    cursor.execute(sql_query)
                
                # Log PostgreSQL notices if any
                if self.connection.notices:
                    logger.info(self.connection.notices[-1])
                    self.connection.notices = []

                self.connection.commit()
                
                if fetch:
                    return cursor.fetchall()
                else:
                    return "QUERY SUCCESS"
        except psycopg2.errors.lookup(psycopg2.errorcodes.UNIQUE_VIOLATION) as e:
            self.connection.rollback()
            logger.error("INSERT ERROR: Unique constraint violated")
            return "INSERT ERROR: " + str(e)
        except Exception as e:
            self.connection.rollback()
            logger.error(f"QUERY ERROR: {e}")
            return f"QUERY ERROR: " + str(e)
