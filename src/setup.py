from openai import OpenAI
from dotenv import load_dotenv
import os 
import mysql.connector

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

db_connection = mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('PASSWORD'),
    database='datawise-db2' #os.getenv('DATABASE')
)