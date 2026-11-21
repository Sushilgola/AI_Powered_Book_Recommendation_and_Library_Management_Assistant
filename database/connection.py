
# database/connection.py

import mysql.connector
import streamlit as st


def get_connection():

    config = st.secrets["mysql"]

    conn = mysql.connector.connect(
        host=str(config["host"]),
        user=str(config["user"]),
        password=str(config["password"]),
        database=str(config["database"]),
        port=int(config["port"])
    )

    return conn
