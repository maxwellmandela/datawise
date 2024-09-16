import json
import numpy as np
from setup import client

# generate SQL query from natural language prompt
def generate_sql(sql_prompt, query):
    response = client.chat.completions.create(
        messages=[
            {
                'role': 'system', 
                'content': 'Generate a SQL query based on the schema provided. \
                    Ensure all required fields are filled for inserts, use necessary joins, and provide only the SQL query.'
            },
            {'role': 'user', 'content': f"Schema:\n{sql_prompt}\nQuery: {query}",},
        ],
        model="gpt-4o-mini",
        temperature=0,
    )

    print("\n USAGE: ", response.usage)
    
    return response.choices[0].message.content.strip()



# Pretty print the condensed schema
def print_condensed_schema(condensed):
    for table, columns in condensed.items():
        print(f"{table}:")
        for col in columns:
            print(f"  - {col}")
        print()

        
if __name__ == "__main__":
    # init_condensation() # Run just once
    with open("app/databases/condensed_schema.json", 'r') as f:
        schema = json.load(f)

        user_query = input("Enter a query: ")

        print(f"\n User query: {user_query}")

        print("\n FINAL QUERY: \t", generate_sql(schema, user_query))
