import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from setup import client

# Load embeddings
def load_embeddings(file_path='schema_embeddings.json'):
    with open(file_path, 'r') as f:
        embeddings = json.load(f)
    return embeddings

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

# Generate embeddings for each schema component in prose format and save the plain text
def initialize_schema_embeddings():
    with open("schema_flip.json", 'r') as f:
        schema = json.load(f)

        # Generate embeddings for each schema component
        embeddings = {}
        plain_texts = {}

        for table, details in schema.items():
            print(f"\nGenerating embeddings for table {table}")

            # Prose for the table
            table_prose = (f"The table '{table}' consists of the following columns: "
                           f"{', '.join([col.split(' ')[0] for col in details['columns']])}.")
            embeddings[table] = get_embedding(table_prose)
            plain_texts[table] = table_prose

            # Prose for columns
            for column in details['columns']:
                col_name = column.split(' ')[0]
                col_description = (f"The column '{col_name}' in the table '{table}' is described as: {column}.")
                embeddings[f"{table}.{col_name}"] = get_embedding(col_description)
                plain_texts[f"{table}.{col_name}"] = col_description

            # Prose for relationships
            if 'relationships' in details:
                for relation in details['relationships']:
                    rel_prose = (f"The table '{table}' is related to the table '{relation['referenced_table_name']}' "
                                 f"through the column '{relation['column_name']}', which references the column "
                                 f"'{relation['referenced_column_name']}' in the '{relation['referenced_table_name']}' table.")
                    embeddings[f"{table}.{relation['referenced_table_name']}_relation"] = get_embedding(rel_prose)
                    plain_texts[f"{table}.{relation['referenced_table_name']}_relation"] = rel_prose

            print(f"Done generating embeddings for table {table}\n")

        # Save embeddings and plain texts to JSON files
        with open('schema_embeddings.json', 'w') as f:
            json.dump(embeddings, f)
            print("Embeddings generated and stored successfully.")

        with open('schema_plain_texts.json', 'w') as f:
            json.dump(plain_texts, f)
            print("Plain texts generated and stored successfully.")

        return embeddings, plain_texts

# Example usage:
initialize_schema_embeddings()
