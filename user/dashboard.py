
# user/dashboard.py

import streamlit as st
from urllib.parse import quote_plus

from database.books import list_books

from database.loans import (
    borrow_book,
    return_book,
    get_user_loans
)

from services.groq_service import get_ai_response


def render_user_dashboard(user):

    st.title("📚 User Dashboard")

    st.caption(f"Welcome, {user['full_name']}")

    notice = st.session_state.pop("user_notice", None)

    if notice:
        st.success(notice)

    chat_tab, search_tab, loans_tab = st.tabs([
        "AI Book Assistant",
        "Find & Borrow Books",
        "My Borrowed Books"
    ])

    # ----------------------------
    # 1. AI Book Assistant
    # ----------------------------

    with chat_tab:

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "Ask about books, authors or recommendations..."
        )

        if prompt:

            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            try:

                with st.chat_message("assistant"):

                    with st.spinner("Thinking..."):

                        response = get_ai_response(
                            st.session_state.chat_history
                        )

                    st.markdown(response)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:

                st.error(f"AI Error: {e}")

    # ----------------------------
    # 2. Search & Borrow Books
    # ----------------------------

    with search_tab:

        st.subheader("Search Library Books")

        search = st.text_input(
            "Search by title or author",
            key="library_search"
        )

        try:

            books = list_books(search.strip())

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

                            st.success("Available to borrow")

                            if st.button(
                                "Borrow Book",
                                key=f"borrow_{book['book_id']}"
                            ):

                                success, message = borrow_book(
                                    book["book_id"],
                                    user["user_id"]
                                )

                                if success:
                                    st.session_state.user_notice = message
                                    st.rerun()

                                else:
                                    st.warning(message)

                        else:

                            st.warning("Currently unavailable")

                        # External ebook reading
                        if book["ebook_url"]:

                            st.link_button(
                                "Read Online",
                                book["ebook_url"]
                            )

                        else:

                            query = quote_plus(book["title"])

                            st.link_button(
                                "Find Online",
                                f"https://books.google.com/books?q={query}"
                            )

            else:

                st.warning(
                    "This book is not in our library database."
                )

                if search.strip():

                    query = quote_plus(search)

                    st.link_button(
                        "Search Google Books",
                        f"https://books.google.com/books?q={query}"
                    )

        except Exception as e:

            st.error(f"Library Error: {e}")

    # ----------------------------
    # 3. My Borrowed Books
    # ----------------------------

    with loans_tab:

        st.subheader("My Borrowing History")

        try:

            loans = get_user_loans(user["user_id"])

            if loans:

                for loan in loans:

                    with st.container(border=True):

                        st.write("Book:", loan["title"])

                        st.write("Borrowed:", loan["borrow_date"])

                        st.write("Due Date:", loan["due_date"])

                        st.write("Status:", loan["status"])

                        if loan["status"] == "BORROWED":

                            if st.button(
                                "Return Book",
                                key=f"return_{loan['loan_id']}"
                            ):

                                success, message = return_book(
                                    loan["loan_id"],
                                    user["user_id"]
                                )

                                if success:
                                    st.session_state.user_notice = message
                                    st.rerun()

                                else:
                                    st.error(message)

            else:

                st.info("You have not borrowed any books yet.")

        except Exception as e:

            st.error(f"Borrowing history error: {e}")
