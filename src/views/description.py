import streamlit as st 
from src.promptinjection import describe_schema
from src.setup import schema


def description():
    if 'data_source_description' not in st.session_state:
        print(f"\n Describe the data...")
        st.session_state.data_source_description = describe_schema(schema, 'describe this db')

    st.write(f"""
        #### Data description: 
        {st.session_state.data_source_description}
        """)
