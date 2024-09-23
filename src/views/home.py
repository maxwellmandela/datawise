import streamlit as st 
from src.promptinjection import generate_sql, generate_table_columns
from src.setup import schema
import ast
import pandas as pd


def run_generated_sql(sql_query, db_conn, cursor):
    cursor.execute(sql_query, multi=True)

    # If it's a SELECT query, fetch and display the results
    if sql_query.strip().lower().startswith("select"):
        results = cursor.fetchall()

        # Generate columns | should be finetuned for column names generation, should also allow sending one of the results
        if len(results):
            columns = generate_table_columns(schema, sql_query, results[0])
            columns = ast.literal_eval(columns)

            print(results)

            df = pd.DataFrame(results, columns=columns)

            # Display the table in Streamlit
            st.write('### Response')
            st.write(df)

            # st.line_chart(df, x='category_name', y='total_products')

            # rerun_query_button = st.button("Re-run database query")
            # if rerun_query_button:
            #     run_generated_sql(sql_query, db_conn, cursor)
        else:
            st.warning('Sorry, that did not return any results')

    else:
        # For INSERT, UPDATE, DELETE queries, commit changes and show success message
        db_conn.commit()
        st.success(f"Query executed successfully")

# Function to handle the query processing
def process_query(schema, user_query, db_conn):
    print(f"User query: {user_query}")
    
    # Generate SQL based on the user input | should be finetuned for sql responses
    ai_response = generate_sql(schema, user_query)

    st.warning(f"""
        #### DEBUG QUERY: 
        {ai_response.replace('```sql', '').replace('```', '')}
        """)
    
    try:
        cursor = db_conn.cursor()
        sql_query = ai_response.replace('```sql', '').replace('```', '')

        run_generated_sql(sql_query, db_conn, cursor)
    except Exception as e:
        st.error(f"Error running query: {e}")
    finally:
        if cursor:
            cursor.close()


# Define views/pages
def home():
    st.write("#### Welcome to DataWise!")
    st.write("Ask a question about your data:")

    user_query = st.text_area("Enter your query:")
    query_button = st.button("Submit", type="primary")

    if query_button and user_query:
        process_query(schema, user_query, st.session_state.db_conn)
