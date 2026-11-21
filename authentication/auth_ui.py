
# authentication/auth_ui.py

import streamlit as st

from authentication.auth import (
    register_user,
    login_user
)


def render_auth_ui():

    st.title("📚 Library Management System")

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    # ------------------------
    # Login Form
    # ------------------------

    with login_tab:

        with st.form("login_form"):

            email = st.text_input("Email")

            password = st.text_input(
                "Password",
                type="password"
            )

            submit = st.form_submit_button("Login")

            if submit:

                user = login_user(email, password)

                if user:

                    st.session_state.current_user = user

                    st.rerun()

                else:

                    st.error("Invalid email or password.")

    # ------------------------
    # Registration Form
    # ------------------------

    with register_tab:

        with st.form("register_form"):

            name = st.text_input("Full Name")

            email = st.text_input("Email Address")

            password = st.text_input(
                "Create Password",
                type="password"
    
            )

            submit = st.form_submit_button("Register")

            if submit:

                success, message = register_user(
                    name, email, password
                )

                if success:
                    st.success(message)

                else:
                    st.error(message)
