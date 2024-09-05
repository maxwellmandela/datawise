import json
from setup import client
from embeddings import get_embedding, cosine_similarity, load_embeddings

def retrieve_relevant_schema(query, embeddings):
    query_embedding = get_embedding(query)
    relevant_tables = set()
    relevant_columns = set()
    
    for component, embedding in embeddings.items():
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        # print("\n", component.split('.')[0], ":", similarity)

        if similarity > 0.2:  # Threshold for relevance
            if '.' in component:
                if '_relation' in component:
                    relevant_tables.add(component.split('.')[0])
                    relevant_tables.add(component.split('.')[1].replace('_relation', ''))
                else:
                    relevant_columns.add(component.split('.')[0])
            else:
                relevant_tables.add(component)
    
    relevant_schema = {table: schema[table] for table in relevant_tables}
    for table in relevant_schema:
        relevant_schema[table]['columns'] = [col for col in relevant_columns if col.startswith(table + '.')]
    return relevant_schema


def load_schema(file_path='schema.json'):
    with open(file_path, 'r') as file:
        schema = json.load(file)
    return schema

def parse_query(query, schema):
    response = client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': f'You are an SQL expert. Use the provided schema to generate SQL queries. \
                            Here is the schema: {json.dumps(schema)}. \
                            Only generate SQL based on this schema. Do not infer any tables or columns not listed in the schema. Return only the SQL query'
            },
            {'role': 'user', 'content': query},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    
    return response.choices[0].message.content.strip()


# TEST
query = input("QUERY: ")
schema = load_schema()

relevant_schema = retrieve_relevant_schema(query, load_embeddings())
print("\nRelevant schema\n", relevant_schema)

parsed_query = parse_query(query, relevant_schema)
print("\n\nParsed Query:\n", parsed_query)
