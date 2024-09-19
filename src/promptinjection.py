import json
import numpy as np
from src.setup import client

def run_prompt(messages):
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0,
    )

    print("\n USAGE: ", response.usage)
    
    return response.choices[0].message.content.strip()


# generate SQL query from natural language prompt
def generate_sql(schema, query: str):
    response = run_prompt([
            {
                'role': 'system', 
                'content': 'Generate a SQL query based on the schema provided. \
                    Ensure all required fields are filled for inserts, use necessary joins, and provide only the SQL query.'
            },
            {'role': 'user', 'content': f"Schema:\n{schema}\nQuery: {query}",},
        ]
    )

    return response


def describe_schema(schema, query: str):
    response = run_prompt([
            {
                'role': 'system', 
                'content': 'You are a database expert. \
                    You can describe in high level the information on a database given the schema.'
            },
            {'role': 'user', 'content': f"Describe what kind of information this database holds given the schema:\n{schema}",},
        ],
        model="gpt-4o-mini",
        temperature=0,
    )

    return response


def generate_table_columns(schema, sql_query: str):
    response = run_prompt([
        {
            'role': 'system', 
            'content': "You are a pandas data expert. \
                        You will return a list of strings representing the column names needed for a pandas dataframe, based on an SQL query. \
                        The list should only include the necessary columns from the SQL statement."
        },
        {
            "role": "user",
            "content": "Generate the necessary columns for the pandas dataframe given this query: SELECT id, name, email FROM customers"
        },
        {
            "role": "system",
            "content": "['id', 'name', 'email']"
        },
        {
            'role': 'user', 
            'content': f"Generate the required columns based on this DB schema:\n{schema}\nand this SQL query:\n{sql_query}"
        },
    ])

    return response



        
if __name__ == "__main__":
    # init_condensation() # Run just once
    with open("app/databases/condensed_schema.json", 'r') as f:
        schema = json.load(f)

        user_query = "SELECT p.name AS product_name, oi.price AS item_price, SUM(oi.quantity) AS total_quantity FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN orders o ON oi.order_id = o.id GROUP BY p.id, oi.price ORDER BY total_quantity DESC;"
        # input("Enter a query: ")

        # print(f"\n User query: {user_query}")

        print("\n FINAL QUERY: \t", generate_table_columns(schema, user_query))
