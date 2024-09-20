from openai import OpenAI
import os 
import mysql.connector
import json
import streamlit as st

client = OpenAI(api_key=os.getenv('DATAWISE_OPENAI_KEY'))

db_connection = mysql.connector.connect(
    host=os.getenv('DATAWISE_HOST'),
    user=os.getenv('DATAWISE_DB_USER'),
    password=os.getenv('DATAWISE_PASSWORD'),
    database=os.getenv('DATAWISE_DATABASE')
)

# Load the schema from a file
with open("src/databases/condensed_schema.json", 'r') as f:
    schema = json.load(f)