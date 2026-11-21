from database.connection import get_connection

# main.py

import streamlit as st

from authentication.auth_ui import render_auth_ui
from admin.dashboard import render_admin_dashboard
from user.dashboard import render_user_dashboard


# ----------------------------
# Page Configuration
# ----------------------------

st.set_page_config(
    page_title="AI Library Management System",
    page_icon="📚",
    layout="wide"
)


# ----------------------------
# Initialize Session
# ----------------------------

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ----------------------------
# Main Application
# ----------------------------

user = st.session_state.current_user


if user is None:

    # Login and Registration
    render_auth_ui()

else:

    # Sidebar
    with st.sidebar:

        st.title("📚 My Library")

        st.write("Name:", user["full_name"])

        st.write("Role:", user["role"].upper())

        if st.button("Logout", use_container_width=True):

            st.session_state.current_user = None
            st.session_state.chat_history = []

            st.rerun()

    # Role-Based Dashboard
    if user["role"] == "admin":

        render_admin_dashboard(user)

    elif user["role"] == "user":

        render_user_dashboard(user)

    else:

        st.error("Invalid account role.")
