import os
import json
from src.setup import db_connection
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to condense the schema to a more concise format for prompt injection
def condense_schema(schema):
    condensed_schema = {}

    for table, details in schema.items():
        condensed_columns = []
        
        for column in details["columns"]:
            # Extract core parts of each column definition
            parts = column.split("(", 1)
            col_name = parts[0].strip()
            rest = parts[1].rstrip(")").split(",") if len(parts) > 1 else []
            
            col_type = rest[0].strip() if rest else "unknown"
            constraints = []

            if "PK" in column or "PRI" in column:
                constraints.append("PK")
            if "auto_increment" in column:
                constraints.append("auto_increment")
            if "FK" in column:
                # Handle FK part separately (this assumes you include FK notation in the original)
                constraints.append("FK")
            if "MUL" in column:
                constraints.append("FK")  # Multiplicity likely indicates FK relationship

            # Combine into concise column info
            col_info = f"{col_name} ({col_type}"
            if constraints:
                col_info += ", " + ", ".join(constraints)
            col_info += ")"

            condensed_columns.append(col_info)

        # Add to condensed schema
        condensed_schema[table] = condensed_columns

    return condensed_schema

# Pretty print the condensed schema
def print_condensed_schema(condensed):
    for table, columns in condensed.items():
        print(f"{table}:")
        for col in columns:
            print(f"  - {col}")
        print()


# Function to fetch table descriptions and relationships
def get_table_descriptions_and_relationships(cursor):
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    schema = {}

    for table in tables:
        table_name = table[0]
        
        # Fetch column descriptions
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()

        schema[table_name] = {
            "columns": [],
            "relationships": []
        }

        for column in columns:
            field = column[0]
            col_type = column[1]
            is_null = "nullable" if column[2] == "YES" else "not nullable"
            key = column[3] if column[3] else ''
            default = f"default={column[4]}" if column[4] else ''
            extra = column[5] if column[5] else ''
            col_description = f"{field} ({col_type}, {is_null}, {key}, {default}, {extra})"
            schema[table_name]["columns"].append(col_description.strip(", "))

        # Fetch foreign key relationships
        cursor.execute(f"""
            SELECT DISTINCT
                k.column_name, k.referenced_table_name, k.referenced_column_name
            FROM
                information_schema.key_column_usage k
            WHERE
                k.table_name = '{table_name}' AND
                k.referenced_table_name IS NOT NULL;
        """)
        relationships = cursor.fetchall()
        
        # Use a set to track seen relationships and avoid duplicates
        seen_relationships = set()
        
        for rel in relationships:
            column_name, ref_table, ref_column = rel
            relationship = (column_name, ref_table, ref_column)
            if relationship not in seen_relationships:
                schema[table_name]["relationships"].append({
                    "column_name": column_name,
                    "referenced_table_name": ref_table,
                    "referenced_column_name": ref_column
                })
                seen_relationships.add(relationship)

    # Save schema to JSON file
    schema_file = 'src/databases/schema.json'
    with open(schema_file, 'w') as file:
        json.dump(schema, file, indent=4)
        print(f"Schema with relationships saved to {schema_file}")

    condensed = condense_schema(schema)
    with open("src/databases/condensed_schema.json", 'w') as f:
        json.dump(condensed, f)
        print(f"Condensed schema saved to condensed_schema.json")


def init_generation():
    cursor = db_connection.cursor()

    # Retrieve table descriptions and relationships
    get_table_descriptions_and_relationships(cursor)
    cursor.close()
    db_connection.close()

if __name__ == "__main__":
    init_generation()
