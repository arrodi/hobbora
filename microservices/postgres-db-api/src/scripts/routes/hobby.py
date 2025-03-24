# routes/user_routes.py
from scripts.util.imports import *

hobby_bp = Blueprint("hobby", __name__)
logger = logging.getLogger(__name__)

@hobby_bp.route("/add", methods=['POST'])
def hobby_add():
    print("/hobby/add")
    request_data = request.get_json()
    request_data["HOBBY_ID"] = str(uuid.uuid4().hex[:6])
    sql_query, sql_values = queries.insert_into_table("USER_HOBBIES", request_data)
    query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@hobby_bp.route("/get", methods=['POST'])
def get_hobby():
    print("/hobby/get")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_context = queries.select_table("USER_HOBBIES", schemas.table_schemas["USER_HOBBIES"].keys(), f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_context, fetch=True)

    print(query_return)

    
    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

        request_data["DATA"] = query_return_lst[0]
    else:
        request_data["DATA"] = {}

    return jsonify(request_data)

@hobby_bp.route("/edit", methods=['POST'])
def edit_hobby():
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.modify_record("USER_HOBBIES", request_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully edit a hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)


@hobby_bp.route("/tutor", methods=['POST'])
def hobby_tutor():

    print("/hobby/tutor")

    request_data = request.get_json()

    print(request_data)

    hobby_id = request_data["HOBBY_ID"]
    change_data = {"TUTORING":True}
    sql_query, sql_values = queries.modify_record("USER_HOBBIES", change_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the tutored hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@hobby_bp.route("/tutored/get", methods=['POST'])
def get_tutored_hobby():
    print("/hobby/tutored/get")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_context = queries.select_table("USER_HOBBIES_TUTORING", schemas.table_schemas["USER_HOBBIES_TUTORING"].keys(), f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_context, fetch=True)

    print(query_return)

    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

        request_data["DATA"] = query_return_lst[0]
        request_data["SUCCESS"] = True
        request_data["SELECT"] = len(query_return_lst[0])
    else:
        request_data["SUCCESS"] = True
        request_data["SELECT"] = "EMPTY"
        request_data["DATA"] = {}

    return jsonify(request_data)

@hobby_bp.route("/tutored/add", methods=['POST'])
def add_tutored_hobby():
    print("/hobby/tutored/add")

    request_data = request.get_json()

    sql_query, sql_values = queries.insert_into_table("USER_HOBBIES_TUTORING", request_data)
    query_return = g.postgres.execute_query(sql_query, sql_values)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the tutored hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@hobby_bp.route("/tutored/edit", methods=['POST'])
def edit_tutored_hobby():
    print("/hobby/tutored/edit")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.modify_record("USER_HOBBIES_TUTORING", request_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_query, sql_values)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully edited a hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)
    
@hobby_bp.route("/delete", methods=['POST'])
def delete_hobby():
    print("/hobby/delete")

    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.delete_record("USER_HOBBIES", f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_query)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully deleted the hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@hobby_bp.route("/tutored/delete", methods=['POST'])
def delete_tutored_hobby():
    print("/hobby/tutored/delete")

    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.delete_record("USER_HOBBIES_TUTORING", f"HOBBY_ID = '{hobby_id}'")
    query_return = g.postgres.execute_query(sql_query)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully deleted the hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)