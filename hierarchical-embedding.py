import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from setup import client

# Load embeddings from file
def load_embeddings(file_path='schema_embeddings.json'):
    with open(file_path, 'r') as f:
        embeddings = json.load(f)
    return embeddings

# Function to get embedding for a text using OpenAI API
def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-large")
    return response.data[0].embedding

# Hierarchical Embeddings Initialization
def initialize_hierarchical_embeddings():
    with open("schema_flip.json", 'r') as f:
        schema = json.load(f)

        embeddings = {}
        
        # Top-level embedding for each table
        for table, details in schema.items():
            table_embedding = get_embedding(f"Table: {table}")
            embeddings[table] = {
                "embedding": table_embedding,
                "columns": {},
                "relationships": {}
            }
            
            # Column embeddings
            for column in details['columns']:
                column_name = column.split('(')[0].strip()
                col_embedding = get_embedding(f"Column: {column_name} in Table: {table}")
                embeddings[table]['columns'][column_name] = col_embedding
            
            # Relationship embeddings
            for rel in details['relationships']:
                rel_text = f"Relation from {table}.{rel['column_name']} to {rel['referenced_table_name']}.{rel['referenced_column_name']}"
                rel_embedding = get_embedding(rel_text)
                rel_key = f"{rel['column_name']}->{rel['referenced_table_name']}.{rel['referenced_column_name']}"
                embeddings[table]['relationships'][rel_key] = rel_embedding

            print(f"Finished processing table: {table}")
        
        # Save embeddings to file
        with open('hierarchical_schema_embeddings.json', 'w') as f:
            json.dump(embeddings, f)
            print("Hierarchical embeddings generated and stored successfully.")
        
        return embeddings

# Function to find related schema components using hierarchical embeddings
def find_related_components(query_embedding, embeddings, threshold=0.8):
    related_components = []

    for table, data in embeddings.items():
        # Compare table embedding
        table_similarity = cosine_similarity([query_embedding], [data['embedding']])[0][0]
        if table_similarity >= threshold:
            related_components.append((table, 'table', table_similarity))
        
        # Compare column embeddings
        for column_name, col_embedding in data['columns'].items():
            col_similarity = cosine_similarity([query_embedding], [col_embedding])[0][0]
            if col_similarity >= threshold:
                related_components.append((f"{table}.{column_name}", 'column', col_similarity))
        
        # Compare relationship embeddings
        for rel_key, rel_embedding in data['relationships'].items():
            rel_similarity = cosine_similarity([query_embedding], [rel_embedding])[0][0]
            if rel_similarity >= threshold:
                related_components.append((f"{table}.{rel_key}", 'relationship', rel_similarity))
    
    related_components.sort(key=lambda x: x[2], reverse=True)
    return related_components

# Example usage
if __name__ == "__main__":
    # Initialize embeddings (run this only once to generate embeddings)
    # initialize_hierarchical_embeddings()

    # Load embeddings
    embeddings = load_embeddings('hierarchical_schema_embeddings.json')

    # # Example query
    query = "all assessments from the vehicle KBK 644T"
    query_embedding = get_embedding(query)

    # # Find related schema components
    related_components = find_related_components(query_embedding, embeddings, 0.45)
    
    print("Related Components:")
    for component, comp_type, similarity in related_components:
        print(f"{comp_type.capitalize()}: {component} (Similarity: {similarity:.2f})")
