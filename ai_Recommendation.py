# first i use gemini api key for generate renponses

import os
# import time
from dotenv import load_dotenv
# from google import genai
from groq import Groq
# from google.genai import errors
from urllib.parse import quote_plus
import mysql.connector
import streamlit as st 
from datetime import date, timedelta
import bcrypt


def register_user(full_name, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, 'user')
            """,
            (full_name, email, password_hash)
        )

        conn.commit()
        return True, "Registration successful!"

    except mysql.connector.IntegrityError:
        conn.rollback()
        return False, "Email already registered."

    finally:
        cursor.close()
        conn.close()

def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM users
        WHERE email = %s AND is_active = TRUE
        """,
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:

        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if password_valid:

            return {
                "user_id": user["user_id"],
                "name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            }

    return None

## Separate Admin and User dashboards
if "current_user" not in st.session_state:
    st.session_state.current_user = None

## After Successful Login
user = login_user(email="sushil@gmail.com", password=123456)

if user:
    st.session_state.current_user = user
    st.rerun()
else:
    st.error("Invalid email or Password")

## Now check the user's Role

if st.session_state.current_user:

    user = st.session_state.current_user

    if user["role"] == "admin":

        st.title("Admin Dashboard")

        # Admin functionality here

    else:

        st.title("User Dashboard")

        # User functionality here

else:

    st.title("Login Page")


ai_tab, library_tab = st.tabs([
    "AI Book Assistant",
    "Find & Borrow Books"
])

with ai_tab:

    st.set_page_config(
        page_title="My AI ChatBot",
        page_icon="🤖",
        layout="centered"
    )

    st.title("My chat Bot")
    st.write("Welcome to my ChatBot")

    @st.cache_resource
    def get_groq_client():
        return Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )


    client = get_groq_client()

    ###  Initialize chat history

    if "message" not in st.session_state:
        st.session_state.messages = []

    # Clear conversation button 

    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    ## Get user Input

    prompt = st.chat_input("Ask Qustions! ")   # create a chat-style imput field 

    if prompt:

        # save message
        st.session_state.messages.append({
            'role':'user',
            'content':prompt
        })

        ## Display user message
        with st.chat_message('user'):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):

            try:
                with st.spinner("Thinking...."):
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                'role':'system',
                                'content':"""
                                You are a helpful AI assistant.
                                Give clear, simple and concise answers.
                                Use headings and bullet points when useful.
                                Avoid unnecessary explainations."""
                            },
                            *st.session_state.messages
                        ],

                        temperature=0.4,
                        max_completion_tokens=600
                    )

                    response = completion.choices[0].message.content
                    st.markdown(response)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

with library_tab:

    def get_connection():
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return connection

    # Write a Search Book Function 
    def search_books(book_name):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT *
                FROM books
                WHERE title LIKE %s
                OR auther LIKE %s
        """

        search_value = f"%{book_name}%"
        cursor.execute(
            query,
            (search_value, search_value)
        )

        books = cursor.fetchall()

        cursor.close()
        conn.close()

        return books

    # Create a function for Borrow the Book
    def borrow_book(book_id, member_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            #check available and reseve one copy 
            cursor.execute(
                """
                UPDATE books
                SET available_copies = available_copies -1
                WHERE book_id = %s
                AND available_copies > 0
                """,
                (book_id,)
            )

            # check whether a copy was successfully reserved
            if cursor.rowcount != 1:
                conn.rollback()
                return False, "Sorry this book no longer available."
            
            # Set borrowing and due dates
            borrow_date = date.today()
            due_date = borrow_date + timedelta(days=14)

            # Insert borrowing and due dates
            cursor.execute(
                """
                INSERT INTO loans
                (book_id, member_id, borrow_date, due_date, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    book_id,
                    member_id,
                    borrow_date,
                    due_date,
                    "BORROWED"
                )
            )

            # Save both database changes
            conn.commit()

            return True, f"Book borrowed successfully! Return by {due_date}."

        except mysql.connector.Error:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()
            

    st.subheader("find & Borrow a Book")

    # Display successful borrowing notification
    if "borrow_notice" in st.session_state:
        st.success(st.session_state.pop("borrow_notice"))

    # Search input
    book_name = st.text_input("Enter Book Name", placeholder="Search for Book...")

    # Demo member ID
    member_id = st.number_input(
        "library member ID",
        min_value=1,
        value=1,
        step=1
    )

    if book_name.strip():

        try:
            books = search_books(book_name.strip())

            if books:

                for book in books:

                    with st.container(border=True):

                        st.subheader(book["title"])

                        st.write("Author:", book["author"])

                        st.write(
                            "Available Copies:",
                            book["available_copies"]
                        )

                        if book["available_copies"] > 0:

                            st.success("Book Available!")

                            if st.button(
                                "Borrow Book",
                                key=f"borrow_{book['book_id']}"
                            ):

                                success, message = borrow_book(
                                    book["book_id"],
                                    int(member_id)
                                )

                                if success:
                                    st.session_state["borrow_notice"] = message
                                    st.rerun()
                                else:
                                    st.warning(message)

                        else:
                            st.warning("Currently Not Available")

                            q = quote_plus(book["title"])

                            st.link_button(
                                "Search on Google Books",
                                f"https://books.google.com/books?q={q}"
                            )

                            st.link_button(
                                "Find on Project Gutenberg",
                                f"https://www.gutenberg.org/ebooks/search/?query={q}"
                            )

            else:

                st.warning(
                    "This book is not available in our library database."
                )

                q = quote_plus(book_name)

                st.link_button(
                    "Search on Google Books",
                    f"https://books.google.com/books?q={q}"
                )

                st.link_button(
                    "Find on Project Gutenberg",
                    f"https://www.gutenberg.org/ebooks/search/?query={q}"
                )

        except mysql.connector.Error as e:

            st.error(f"Database Error: {e}")


    # Login and registration forms here

# if st.button("Generate Response"):
#     st.write(result)

# response = client.chat.completions.create(
#     model="openai/gpt-oss-120b",
#     messages=[
#         {'role':'user', 
#         'content': prompt}
#     ],
#     temperature=0.3,
# )
# result = response.choices[0].message.content


    
    # print(response.choices[0].message.content)
    # n_pmt = input("\nYou: ")

    # if n_pmt.lower() in ['exit', 'quit']:
    #     print("GoodBye!")
    #     break


    # except errors.ServerError as e:
    #     print("Server error. Attempt ", attempt+1, "/5")

    #     if attempt == 2:
    #         print("Gemini server is temporarily unavailable.")
    #         raise
    #     time.sleep(5 * (attempt+1))