# routes/user_routes.py
from scripts.util.imports import *

catalog_bp = Blueprint("catalog", __name__)
logger = logging.getLogger(__name__)

@catalog_bp.route("/hobbies/get", methods=['GET'])
#Returns all information on a single hobby
def catalog_hobbies_get():
    print("/catalog/hobbies/get")
    try: 
        where_clause_string = ""
        ##['name', 'type', 'experience_years', 'proficiency', 'hourly_rate', 'mode_live_call', 'mode_public_in_person', 'mode_private_in_person']:
        param_dict = request.args.to_dict()
        print(param_dict)
        if param_dict.get("HIDE_MY_HOBBIES") == 'true':
            user_id = param_dict["USER_ID"]
            where_clause_string += f"a.USER_ID!='{user_id}'"
        if param_dict.get("USER_ID"):  
            del param_dict["USER_ID"]
        if param_dict.get("HIDE_MY_HOBBIES"):
            del param_dict["HIDE_MY_HOBBIES"]

        for key in param_dict:
            if key.upper() == 'NAME':
                where_clause_string += f"a.NAME IS NOT NULL AND a.NAME LIKE '%{param_dict[key]}%'"
            elif key.upper() == 'PROFICIENCY':
                if param_dict[key].upper() == "ANY":
                    continue
                else:
                    if where_clause_string:  # Add a comma separator if the string already has content
                        where_clause_string += " AND "
                    where_clause_string += f"a.{key}='{param_dict[key]}'"
            elif key.upper() == 'EXPERIENCE_YEARS':
                if where_clause_string:  # Add a comma separator if the string already has content
                    where_clause_string += " AND "
                where_clause_string += f"a.{key}>={param_dict[key]}"
            elif key.upper() == 'HOURLY_RATE':
                if where_clause_string:  # Add a comma separator if the string already has content
                    where_clause_string += " AND "
                where_clause_string += f"b.{key}<={param_dict[key]}"
            else:
                if where_clause_string:  # Add a comma separator if the string already has content
                    where_clause_string += " AND "
                if key in list(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys()):
                    if "text" in schemas.table_schemas["USER_HOBBIES_TUTORING"][key]:
                        where_clause_string += f"b.{key}='{param_dict[key]}'"
                    else:
                        where_clause_string += f'b.{key}={param_dict[key]}'
                if key in list(schemas.table_schemas["USER_HOBBIES"].keys()):
                    if "text" in schemas.table_schemas["USER_HOBBIES"][key]:
                        where_clause_string += f"a.{key} = '{param_dict[key]}'"
                    else:
                        where_clause_string += f"a.{key} = {param_dict[key]}"

        if where_clause_string:
            where_clause_string = "a.TUTORING = true AND " + where_clause_string
        else:
            where_clause_string = "a.TUTORING = true"

        USER_HOBBIES_TUTORING_lst = list(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys())
        USER_HOBBIES_lst = list(schemas.table_schemas["USER_HOBBIES"].keys())

        USER_HOBBIES_ALL_lst = USER_HOBBIES_TUTORING_lst
        USER_HOBBIES_ALL_lst.extend(USER_HOBBIES_lst)

        for _index, _column in enumerate(USER_HOBBIES_TUTORING_lst):
            if _column in USER_HOBBIES_lst:
                USER_HOBBIES_ALL_lst[_index] = f"a.{_column}"
            if _column in USER_HOBBIES_TUTORING_lst:
                USER_HOBBIES_ALL_lst[_index] = f"b.{_column}"

        USER_HOBBIES_COMBINED_SET = set(USER_HOBBIES_ALL_lst)

        request_columns = list(USER_HOBBIES_COMBINED_SET)

        sql_query = queries.select_join_table("USER_HOBBIES", "USER_HOBBIES_TUTORING", request_columns, "HOBBY_ID", where_clause_string)
        
        query_return = g.postgres.execute_query(sql_query, fetch=True)

        print("--QUERY RETURN: " + str(query_return))
        

        request_columns = [_column.replace("a.", "") for _column in request_columns]

        return_data = {}
        if query_return:
            query_return_lst = []
            for _record in query_return:
                _temp_dict = {}
                for _index, _column in enumerate(request_columns):
                    _temp_dict[_column] = _record[_index]
                query_return_lst.append(_temp_dict)
            
            return_data["SUCCESS"] = True
            return_data["MESSAGE"] = "Pulled: " + str(len(query_return_lst)) + " number of records."
            return_data["DATA"] = query_return_lst
        else:
            return_data["SUCCESS"] = True
            return_data["MESSAGE"] = "Query returned no results."
            return_data["DATA"] = []
        return jsonify(return_data)

    #TODO fix this error handling
    except FileNotFoundError as e:
        return_data["SUCCESS"] = False
        return_data["MESSAGE"] = str(e)
        return_data["DATA"] = []
        return jsonify(return_data)