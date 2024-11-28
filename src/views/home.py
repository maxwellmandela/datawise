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

            col1, col2 = st.columns(2)
           
            columns = generate_table_columns(schema, sql_query, results[0])
            columns = ast.literal_eval(columns)

            df = pd.DataFrame(results, columns=columns)

            # Display the table in Streamlit
            with col1:
                st.write('### Response')
                st.write(df)

            # Determine available numeric and categorical columns
            with col2:
                numeric_columns = df.select_dtypes(include='number').columns.tolist()
                categorical_columns = df.select_dtypes(exclude='number').columns.tolist()

                # Display dropdown for chart type selection
                chart_type = st.selectbox("Select chart type:", ["Bar Chart", "Line Chart", "Pie Chart"])

                if chart_type and numeric_columns and categorical_columns:
                    st.write('### Visualize')

                    print("CATEGORICAL CLMNS: ", categorical_columns)
                    print("NUMERIC CLMNS: ", numeric_columns)

                    # Dropdowns to let the user choose categorical and numerical columns
                    selected_category = st.selectbox("Select categorical column:", categorical_columns)
                    selected_numeric = st.selectbox("Select numerical column:", numeric_columns)

                    # Create the chart based on user's selections
                    if chart_type == "Bar Chart":
                        st.bar_chart(df[[selected_category, selected_numeric]].set_index(selected_category))
                    elif chart_type == "Line Chart":
                        st.line_chart(df[[selected_category, selected_numeric]].set_index(selected_category))
                    elif chart_type == "Pie Chart":
                        # For pie chart, show the pie chart using Matplotlib
                        pie_data = df[[selected_category, selected_numeric]].groupby(selected_category).sum()
                        st.write(pie_data)
                        
                        pie_chart = pie_data.plot.pie(y=selected_numeric, autopct='%1.1f%%', figsize=(5, 5))
                        st.pyplot(pie_chart.figure)
            
        # else:
        #     st.warning('Sorry, that did not return any results')

    else:
        # For INSERT, UPDATE, DELETE queries, commit changes and show success message
        # db_conn.commit()
        # st.success(f"Query executed successfully")
        pass

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
