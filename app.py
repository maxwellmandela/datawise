import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from setup import client
from embeddings import get_embedding, load_embeddings, initialize_schema_embeddings

# Load the embeddings from the saved JSON file  | should be a vecotr DB!

# initialize_schema_embeddings() # run once, or when schema is updated

embeddings = load_embeddings('schema_embeddings.json')

def parse_query(query):
    response = client.chat.completions.create(
        messages=[
            {
                'role': 'system', 
                'content': 'From a natural language question, generate a SQL query based on the schema provided of tables and columns and relations. \
                    You should use neccessary joins to achieve this. Reason logically based on provided schema and answer the question with only the SQL query to be run.'
            },

            # {'role': 'user', 'content': 'How many times has the product "kids baby cussions oil" been bought last week?'},
            # {'role': 'system', 'content': "SELECT COUNT(*) AS purchase_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id \
            #     JOIN orders o ON oi.order_id = o.order_id WHERE p.name = 'kids baby cussions oil' AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"},

            # {'role': 'user', 'content': 'Show me the list of customers that bought "Mens wallet" last week'},
            # {'role': 'system', 'content': "SQL: SELECT c.customer_id, c.customer_name \
            #     FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id OIN products p ON oi.product_id = p.product_id \
            #     WHERE p.name LIKE 'Mens wallet' AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"},

            # {'role': 'user', 'content': 'I want to see the customers whose emails have a charity.co.ke work emails'},
            # {'role': 'system', 'content': "SELECT * FROM customers WHERE email LIKE '%@charity.co.ke';"},
            {'role': 'user', 'content': query},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    
    return response.choices[0].message.content.strip()


def match_query_to_schema(parsed_query, embeddings):
    parsed_embedding = get_embedding(parsed_query)
    best_match = None
    best_similarity = -1
    
    for component, embedding in embeddings.items():
        similarity = cosine_similarity([parsed_embedding], [embedding])[0][0]
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = component
    
    return best_match, best_similarity


# Now custom logic based on extracted components, ueful for avoiding UI completely ;)
def generate_sql(matched_component, query_details):
    # Example logic, adjust based on your schema
    sql = ""
    if "customers" in matched_component:
        sql = f"SELECT * FROM customers WHERE {query_details['date_range']} AND {query_details['purchase_condition']}"
    return sql


# TEST
query = input("QUERY: ")
# query = "Create a customer called john with email john@example.com"
# query = "Show me the list of customers from January to December who have made regular purchases."
# query = "How many times has the product 'kids baby cussions oil' been bought last week?"
# parsed_query = parse_query(query)
# print("\QUERY RESULT:", parsed_query)


# ANALYZE & EXTRACT COMPONENTS 
# ===================================================================================================
matched_component, similarity = match_query_to_schema(query, embeddings)
print(f"Best Match: {matched_component} with similarity {similarity}")

# query_details = {
#     "date_range": "purchase_date BETWEEN '2024-01-01' AND '2024-12-31'",
#     "purchase_condition": "COUNT(purchase_id) > 1"
# }
# sql_query = generate_sql(matched_component, query_details)
# print(f"Generated SQL: {sql_query}")


