import streamlit as st
from sidebar import not_authenticated, authenticated

st.set_page_config(page_title="Home Page")

if "token" not in st.session_state:
    not_authenticated()
else:
    authenticated()

st.title("TaskManager")


st.markdown(
    """
    Welcome to our Project Management Application! This application provides a platform for efficient 
    project organization and task management.

    Here you can:
    * Create, view, and manage projects.
    * Add tasks to each project and assign them to team members.
    """
)
