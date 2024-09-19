from src.promptinjection import generate_sql, describe_schema, generate_table_columns
import json 
from src.setup import db_connection
import pandas as pd
import streamlit as st
import ast 

# Load the schema from a file
with open("src/databases/condensed_schema.json", 'r') as f:
    schema = json.load(f)

st.write(""" 
    # DataWise
    Source agnostic data analysis
    """)

def describe_database():
    st.write(f"""
        #### Data description: 
        {describe_schema(schema, 'describe this db')}
        """)

# Function to handle the query when the user presses Enter
def process_query(schema, user_query, db_conn):
    print(f"User query: {user_query}")
    
    # Generate SQL based on the user input
    ai_response = generate_sql(schema, user_query)
    
    st.warning(f"""
        #### DEBUG QUERY: 
        {ai_response.replace('```sql', '').replace('```', '')}
        """)
    
    try:
        # Open a new cursor for the query
        cursor = db_conn.cursor()
        query = ai_response.replace('```sql', '').replace('```', '')
        cursor.execute(query)

        # Check if the query is a SELECT, INSERT, UPDATE, or DELETE
        if query.strip().lower().startswith("select"):
            # If it's a SELECT query, fetch and display the results
            results = cursor.fetchall()

            # Generate columns
            columns = generate_table_columns(schema, query)
            columns = ast.literal_eval(columns)
            df = pd.DataFrame(results, columns=columns)

            # Display the table in Streamlit
            st.write('### Response')
            st.table(df)
        else:
            # For INSERT, UPDATE, DELETE queries, commit changes and show success message
            db_conn.commit()  # Commit changes using the connection object
            st.success(f"Query executed successfully")
                
    except Exception as e:
        st.error(f"Error running query: {e}")
    finally:
        if cursor:
            cursor.close()  # Close the cursor after executing the query

# Persistent database connection
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = db_connection

# Input field for the query, and trigger the process_query function upon Enter
user_query = st.text_input("Ask a question to chat with the data: ")

# Only process if there is user input
if user_query:
    print(f"\n USER: {user_query}")
    process_query(schema, user_query, st.session_state.db_conn)
