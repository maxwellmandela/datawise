import os
import json
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connect to MySQL database using environment variables
conn = mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE')
)
cursor = conn.cursor()

# Function to fetch table descriptions and relationships
def get_table_descriptions_and_relationships(cursor):
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    schema = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()

        schema[table_name] = []

        for column in columns:
            field = column[0]
            col_type = column[1]
            is_null = "nullable" if column[2] == "YES" else "not nullable"
            key = column[3] if column[3] else ''
            default = f"default={column[4]}" if column[4] else ''
            extra = column[5] if column[5] else ''
            col_description = f"{field} ({col_type}, {is_null}, {key}, {default}, {extra})"
            schema[table_name].append(col_description.strip(", "))

    return schema

# Retrieve table descriptions and relationships
schema = get_table_descriptions_and_relationships(cursor)
cursor.close()
conn.close()

# Save schema to JSON file
schema_file = 'schema.json'
with open(schema_file, 'w') as file:
    json.dump(schema, file, indent=4)

print(f"Schema saved to {schema_file}")
