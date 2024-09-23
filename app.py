import streamlit as st

from dotenv import load_dotenv
load_dotenv()
from src.setup import db_connection
from src.views.settings import settings
from src.views.home import home
from src.views.description import description

st.set_page_config(layout="wide")
st.title('DataWise - SQL for humans')


# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # Default page is home

def navigate_to(page):
    """Helper function to update session state for navigation"""
    st.session_state.page = page

# Sidebar navigation menu
with st.sidebar:
    st.write("""
        # DataWise
        Turning everyone into a database expert.
        Supports both Reading & Writing data for RDBMs using SQL
        """)
    
    st.write("##")

    st.write("### Menu")
    
    if st.button('View data description'):
        navigate_to('description')
    
    if st.button('Chat & Analyze'):
        navigate_to('search')
    
    if st.button('Data source settings'):
        navigate_to('settings')

    st.write("""##""")

    st.write("""
             ### Current limits
             - Limited to tabular view
             - Limit single query results
             - WRITE ability is in beta
             - RLHF
             """)


# Persistent database connection
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = db_connection


# Conditional rendering based on the current page
if st.session_state.page == 'home':
    home()
elif st.session_state.page == 'description':
    description()
elif st.session_state.page == 'search':
    home()  # You can reuse the home() function for search & analyze or customize it
elif st.session_state.page == 'settings':
    settings()
