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
    with open("schema.json", 'r') as f:
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
# initialize_schema_embeddings()
 

# Application of the embveddings created above
def search_relevant_tables(query_embedding, schema_embeddings, top_n=5):
    table_scores = {}
    
    # Compare the query embedding with each schema embedding
    for table, embedding in schema_embeddings.items():
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        table_scores[table] = similarity
    
    # Sort tables by similarity score and return the top N
    sorted_tables = sorted(table_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_tables[:top_n]  # Return top N relevant tables

# Load schema embeddings
schema_embeddings = load_embeddings()

# Search for relevant tables
def get_query_embedding(query):
    return get_embedding(query)

user_query = "list all posts created in october 2023"
query_embedding = get_query_embedding(user_query)
relevant_tables = search_relevant_tables(query_embedding, schema_embeddings)

def prepare_sql_generation_prompt(relevant_tables, schema_plain_texts):
    prompt_parts = []
    
    for table, score in relevant_tables:
        if table in schema_plain_texts:
            prompt_parts.append(schema_plain_texts[table])
    
    prompt = "\n".join(prompt_parts)
    return prompt

# Load plain texts
with open('schema_plain_texts.json', 'r') as f:
    schema_plain_texts = json.load(f)

# Prepare the prompt for SQL generation
sql_prompt = prepare_sql_generation_prompt(relevant_tables, schema_plain_texts)

print(f"\n User query: \t {user_query}")
print(f"\n Relevant tables: \t {relevant_tables}")
print(f"\n Prompt for injection: \t", sql_prompt)

def parse_query(sql_prompt, query):
    response = client.chat.completions.create(
        messages=[
            {
                'role': 'system', 
                'content': 'From a natural language question, generate a SQL query based on the schema provided of tables and columns and relations. \
                    You should use neccessary joins to achieve this. Reason logically based on provided schema and answer the question with only the SQL query to be run.'
            },
            {'role': 'user', 'content': f"Generate a SQL query for the following schema:\n{sql_prompt}\nQuery: {query}",},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    
    return response.choices[0].message.content.strip()


print("\n FINAL QUERY: \t", parse_query(sql_prompt, user_query))
