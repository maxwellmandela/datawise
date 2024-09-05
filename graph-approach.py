import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize the graph
schema_graph = nx.Graph()

# Example: Add nodes (tables) and edges (relationships)
# Replace this with dynamic construction from your schema
schema_graph.add_node("assessment")
schema_graph.add_node("repair")
schema_graph.add_edge("repair", "repair_authority", relation="assessment_id")

schema_graph.add_node("approval_metric")
schema_graph.add_node("approval_metric_user")
schema_graph.add_edge("approval_metric", "approval_metric_user", relation="approval_metric_id")

# Generate embeddings (you would use your embedding function here)
def get_embedding(text):
    # Replace with actual embedding function
    return np.random.rand(1, 768)

table_embeddings = {
    table: get_embedding(f"Table: {table}")
    for table in schema_graph.nodes()
}

# Function to perform graph-based search
def search_related_tables(query):
    query_embedding = get_embedding(query)
    
    # Find the closest table to the query using cosine similarity
    closest_table = max(
        table_embeddings,
        key=lambda table: cosine_similarity(query_embedding, table_embeddings[table])
    )
    
    # BFS from the closest table to explore related tables
    visited = set()
    related_tables = []
    queue = [closest_table]
    
    while queue:
        current_table = queue.pop(0)
        if current_table not in visited:
            visited.add(current_table)
            related_tables.append(current_table)
            for neighbor in schema_graph.neighbors(current_table):
                queue.append(neighbor)
    
    return related_tables

# Example Query
query = "List all users with approval authority matrices of more than KES 200,000"
related_tables = search_related_tables(query)
print("Related tables:", related_tables)
