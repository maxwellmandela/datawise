import os
from dotenv import load_dotenv, set_key
import streamlit as st
from src.schema.generator import init_generation

# Ensure the .env file is loaded
dotenv_path = ".env"
load_dotenv(dotenv_path)

def settings():
    st.write("#### Data source settings")
    st.write("Here you can set environment variables like OpenAI API key, DB credentials, etc.")

    # Fetch existing values from the .env file
    openai_key = os.getenv('DATAWISE_OPENAI_KEY', '')
    host = os.getenv('DATAWISE_HOST', 'localhost')
    db_user = os.getenv('DATAWISE_DB_USER', 'admin')
    password = os.getenv('DATAWISE_PASSWORD', 'password')
    database = os.getenv('DATAWISE_DATABASE', 'datawise-db2')
    port = os.getenv('DATAWISE_PORT', '3306')

    # Create input fields for each environment variable
    new_openai_key = st.text_input("OpenAI API Key", value=openai_key)

    col1,col2 = st.columns([4,2])

    with col1:
        st.write("""
                #### DB Credentials
                """)
        new_host = st.text_input("Host", value=host)
        new_db_user = st.text_input("DB User", value=db_user)
        new_password = st.text_input("Password", value=password, type="password")
        new_database = st.text_input("Database", value=database)
        new_port = st.text_input("Port", value=port)

        # Save button
        if st.button("Save Settings", type="primary"):
            # Update the .env file with new values
            set_key(dotenv_path, "DATAWISE_OPENAI_KEY", new_openai_key)
            set_key(dotenv_path, "DATAWISE_HOST", new_host)
            set_key(dotenv_path, "DATAWISE_DB_USER", new_db_user)
            set_key(dotenv_path, "DATAWISE_PASSWORD", new_password)
            set_key(dotenv_path, "DATAWISE_DATABASE", new_database)
            set_key(dotenv_path, "DATAWISE_PORT", new_port)

            st.success("Settings saved successfully!")

    with col2:
        st.write("""
                #### Training
                Helps the AI agent understand the database structure to produce near accurate queries
                """)
        if st.button("Start training"):
            # Update the .env file with new values
            init_generation()
            st.success("Training completed successfully!")
