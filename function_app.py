import azure.functions as func
import datetime
import json
import logging
import os
import re
import snowflake.connector

app = func.FunctionApp()

@app.function_name('RecordChange')
@app.route('recordchange')
def record_change(req: func.HttpRequest) -> func.HttpResponse:
    # Get the environment variables
    USER = os.getenv("SNOWFLAKE_USER")
    PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    DEV_SCHEMA = os.getenv("SNOWFLAKE_DEV_SCHEMA")
    LIVE_SCHEMA = os.getenv("SNOWFLAKE_LIVE_SCHEMA", DEV_SCHEMA)
    WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")

    # Make sure the request is a POST request
    if req.method != "POST":
        returned = { "error": "Only POST requests are allowed" }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=405
        )

    # Make sure the request body is JSON formatted and parse it
    try:
        req_body = req.get_json()
    except ValueError:
        returned = { "error": "Request body does not contain valid JSON" }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=400
        )
    # Make sure the request body contains the required fields
    if "app_type" not in req_body or "record_then" not in req_body or "record_now" not in req_body:
        returned = {
            "error": "Request body must contain the following: app_type, record_then, record_now" 
        }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=400
        )
    
    if req_body["app_type"].lower().startswith("live"):
        schema = LIVE_SCHEMA
    else:
        schema = DEV_SCHEMA
        # Log the request body
        logging.info(f"Request body: {json.dumps(req_body)}")

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user = USER,
        password = PASSWORD,
        account = ACCOUNT,
        database = DATABASE,
        schema = schema,
        warehouse = WAREHOUSE
    )

    # Create the columns text for the table query
    columns_text = ""
    for key in req_body["record_now"]:
        column = re.sub('[^A-Za-z0-9 _]+', '_', key)
        columns_text += f"{column} VARCHAR, "

    # Change the app type to a valid table name
    table_name = req_body["app_type"].upper()
    table_name = "RAW_" + re.sub('[^A-Za-z0-9 _]+', '_', table_name)

    query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_text[:-2]}
            );
            """
    # Create the table if it doesn't exist
    conn.cursor().execute(query)

    # Determine if the record is being created updated or deleted, execute the appropriate query
    if req_body["record_then"]["id"] is None:
        create_record(conn, table_name, req_body["record_now"])
    elif req_body["record_now"]["id"] is None:
        delete_record(conn, table_name, req_body["record_then"]["id"])
    else:
        update_record(conn, table_name, req_body["record_now"])

    return func.HttpResponse(
        json.dumps({ "success": True }),
        mimetype="application/json",
        status_code=200
    )

@app.function_name('FullTableSync')
@app.route('fulltablesync')
def full_table_sync(req: func.HttpRequest) -> func.HttpResponse:
    # Get the environment variables
    USER = os.getenv("SNOWFLAKE_USER")
    PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    DEV_SCHEMA = os.getenv("SNOWFLAKE_DEV_SCHEMA")
    LIVE_SCHEMA = os.getenv("SNOWFLAKE_LIVE_SCHEMA", DEV_SCHEMA)
    WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")

    # Make sure the request is a POST request
    if req.method != "POST":
        logging.warning("Only POST requests are allowed")
        returned = { "error": "Only POST requests are allowed" }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=405
        )
    
    # Make sure the request body is JSON formatted and parse it
    try:
        req_body = req.get_json()
    except ValueError:
        logging.warning("Request body does not contain valid JSON")
        returned = { "error": "Request body does not contain valid JSON" }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=400
        )
    
    if "app_type" not in req_body or "records" not in req_body:
        logging.warning("Request body must contain the following: app_type, records")
        returned = {
            "error": "Request body must contain the following: app_type, records" 
        }
        return func.HttpResponse(
            json.dumps(returned),
            mimetype="application/json",
            status_code=400
        )
    
    if req_body["app_type"].lower().startswith("live"):
        schema = LIVE_SCHEMA
    else:
        schema = DEV_SCHEMA
    
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user = USER,
        password = PASSWORD,
        account = ACCOUNT,
        database = DATABASE,
        schema = schema,
        warehouse = WAREHOUSE
    )

    logging.info("Connected to Snowflake")

    # Change the app type to a valid table name
    table_name = req_body["app_type"].upper()
    table_name = "RAW_" + re.sub('[^A-Za-z0-9 _]+', '_', table_name)

    # Check if the table exists
    query = f"""
            SHOW TABLES LIKE '{table_name}';
            """

    result = conn.cursor().execute(query).fetchone()
    if result is not None:
        if len(req_body["records"]) == 0:
            logging.info("Records list is empty, truncating table")
            query = f"""
                    DELETE FROM {table_name};
                    """
            return func.HttpResponse(
                json.dumps({ "success": True }),
                mimetype="application/json",
                status_code=200
            )
        
        logging.info(f"Table {table_name} exists, syncing records")
        # Create a temporary table to store the records
        columns_text = ""
        columns_list = []
        columns_text += "id VARCHAR UNIQUE PRIMARY KEY, "
        for key in req_body["records"][0]:
            column = re.sub('[^A-Za-z0-9 _]+', '_', key)
            columns_list.append(column)
            if column != "id":
                columns_text += f"{column} VARCHAR, "

        # Check if the columns in the table match the columns in the records
        table_columns_list = []
        results = conn.cursor().execute("SHOW COLUMNS IN TABLE CUSTOM_TESTTYPE;").fetchall()
        for rec in results:
            table_columns_list.append(rec[2])

        # Add columns that are in the records but not in the table
        for column in columns_list:
            if column not in table_columns_list:
                query = f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN {column} VARCHAR;
                        """
                conn.cursor().execute(query)
        
        query = f"""
                CREATE OR REPLACE TABLE TEMP_{table_name} (
                    {columns_text[:-2]}
                );
                """
        conn.cursor().execute(query)

        # Insert the records into the temporary table
        create_multiple_records(conn, f"TEMP_{table_name}", req_body["records"])

        # Delete records that are not in the temporary table
        query = f"""
                DELETE FROM {table_name}
                WHERE id NOT IN (
                    SELECT id FROM TEMP_{table_name}
                );
                """
        conn.cursor().execute(query)

        # Merge the records from the temporary table into the main table
        merge_temp_table(conn, table_name, columns_list)

        # Drop the temporary table
        query = f"""
                DROP TABLE TEMP_{table_name};
                """
        conn.cursor().execute(query)
    else:
        if len(req_body["records"]) == 0:
            logging.info("Records list is empty, no action needed")
            return func.HttpResponse(
                json.dumps({ "success": True }),
                mimetype="application/json",
                status_code=200
            )
        logging.info(f"Table {table_name} does not exist, creating table and syncing records")
        # Create the columns text for the table query
        columns_text = ""
        columns_text += "id VARCHAR, "
        for key in req_body["records"][0]:
            if key != "id":
                # make the column name a valid snowflake identifier
                column_text = re.sub('[^A-Za-z0-9 _]+', '_', key) 
                columns_text += f"{key} VARCHAR, "

        query = f"""
                CREATE TABLE {table_name} (
                    {columns_text[:-2]}
                );
                """
        conn.cursor().execute(query)

        # Insert the records into the table
        create_multiple_records(conn, table_name, req_body["records"])

    return func.HttpResponse(
        json.dumps({ "success": True }),
        mimetype="application/json",
        status_code=200
    )

def create_record(connection: snowflake.connector.SnowflakeConnection, table_name, new_record):
    logging.info(f"Creating record in {table_name} with id: {new_record['id']}")
    columns_text = ""
    values_text = ""
    values_list = []

    for key, value in new_record.items():
        column = re.sub('[^A-Za-z0-9 _]+', '_', key)
        columns_text += f"{column}, "
        values_text += "%s, "
        values_list.append(str(value))

    # Check if the record already exists
    query = f"""
            SELECT * FROM {table_name}
            WHERE id = %s;
            """

    result = connection.cursor().execute(query, new_record["id"]).fetchone()
    if result is not None:
        logging.info(f"Record with id {new_record['id']} already exists")
        return

    query = f"""
            INSERT INTO {table_name} ({columns_text[:-2]})
            VALUES ({values_text[:-2]});
            """
    connection.cursor().execute(query, values_list)

def create_multiple_records(connection: snowflake.connector.SnowflakeConnection, table_name, new_records):
    logging.info(f"Creating records in {table_name}")
    columns_text = ""
    values_text = ""
    all_values_text = ""
    values_list = []

    for key in new_records[0]:
        column = re.sub('[^A-Za-z0-9 _]+', '_', key)
        columns_text += f"{column}, "
        values_text += "%s, "

    for record in new_records:
        for key, value in record.items():
            values_list.append(str(value))
        all_values_text += f"({values_text[:-2]}), "

    query = f"""
            INSERT INTO {table_name} ({columns_text[:-2]})
            VALUES {all_values_text[:-2]};
            """

    connection.cursor().execute(query, values_list)

def merge_temp_table(connection: snowflake.connector.SnowflakeConnection, table_name, columns):
    logging.info(f"Merging records from TEMP_{table_name} into {table_name}")
    set_text = ""
    insert_text = ""
    values_text = ""
    for column in columns:
        if column != "id":
            set_text += f"{column} = TEMP_{table_name}.{column}, "
        insert_text += f"{column}, "
        values_text += f"TEMP_{table_name}.{column}, "

    query = f"""
            MERGE INTO {table_name}
            USING TEMP_{table_name}
            ON {table_name}.id = TEMP_{table_name}.id
            WHEN MATCHED THEN
                UPDATE SET {set_text[:-2]}
            WHEN NOT MATCHED THEN
                INSERT ({insert_text[:-2]})
                VALUES ({values_text[:-2]});
            """
    connection.cursor().execute(query)


def update_record(connection: snowflake.connector.SnowflakeConnection, table_name, record_now):
    logging.info(f"Updating record in {table_name} with id: {record_now['id']}")
    set_text = ""
    values_list = []
    # Create the set text for the query
    for key, value in record_now.items():
        column = re.sub('[^A-Za-z0-9 _]+', '_', key)
        if column != "id":
            set_text += f"{column} = %s, "
            values_list.append(str(value))
    values_list.append(record_now["id"])

    # Check if the record exists
    query = f"""
            SELECT * FROM {table_name}
            WHERE id = %s;
            """

    result = connection.cursor().execute(query, record_now["id"]).fetchone()
    if result is None:
        logging.info(f"Record with id {record_now['id']} does not exist")
        create_record(connection, table_name, record_now)

    query = f"""
            UPDATE {table_name}
            SET {set_text[:-2]}
            WHERE id = %s;
            """
    connection.cursor().execute(query, values_list)

def delete_record(connection: snowflake.connector.SnowflakeConnection, table_name, record_id):
    query = f"""
            DELETE FROM {table_name}
            WHERE id = %s;
            """

    connection.cursor().execute(query, record_id)

