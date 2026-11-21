
# admin/dashboard.py

import streamlit as st

from database.books import (
    list_books,
    add_book,
    update_book,
    set_book_active
)

from database.admin_operations import (
    list_users,
    set_user_active
)

from database.loans import get_all_loans


def render_admin_dashboard(user):

    # Access control
    if user.get("role") != "admin":
        st.error("Admin access required.")
        return

    st.title("🛡️ Admin Dashboard")

    st.caption(f"Welcome, {user['full_name']}")

    overview, add, manage, users_tab, loans_tab = st.tabs([
        "Overview",
        "Add Book",
        "Manage Books",
        "Manage Users",
        "Borrowing Records"
    ])

    # ----------------------------
    # 1. Overview
    # ----------------------------

    with overview:

        books = list_books()
        users = list_users()
        loans = get_all_loans()

        active_loans = [
            loan for loan in loans
            if loan["status"] == "BORROWED"
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric("Available Library Titles", len(books))
        col2.metric("Registered Accounts", len(users))
        col3.metric("Active Borrowings", len(active_loans))

        st.subheader("Recent Borrowing Records")

        st.dataframe(
            loans[:10],
            use_container_width=True,
            hide_index=True
        )

    # ----------------------------
    # 2. Add Book
    # ----------------------------

    with add:

        st.subheader("Add New Book")

        with st.form("add_book_form"):

            title = st.text_input("Book Title")
            author = st.text_input("Author")
            isbn = st.text_input("ISBN")
            description = st.text_area("Description")

            total_copies = st.number_input(
                "Total Copies",
                min_value=1,
                value=1,
                step=1
            )

            ebook_url = st.text_input("Online Reading URL")

            submit = st.form_submit_button("Add Book")

            if submit:

                try:

                    if not title.strip() or not author.strip():
                        st.error("Title and author are required.")

                    else:

                        success, message = add_book(
                            title.strip(),
                            author.strip(),
                            isbn.strip(),
                            description,
                            int(total_copies),
                            ebook_url.strip()
                        )

                        if success:
                            st.success(message)

                except Exception as e:
                    st.error(f"Could not add book: {e}")

    # ----------------------------
    # 3. Manage Books
    # ----------------------------

    with manage:

        st.subheader("Manage Library Books")

        books = list_books(include_inactive=True)

        if books:

            book_map = {
                book["book_id"]: book
                for book in books
            }

            selected_id = st.selectbox(
                "Select Book",
                options=list(book_map.keys()),
                format_func=lambda x: (
                    f"{book_map[x]['title']} (ID: {x})"
                )
            )

            book = book_map[selected_id]

            with st.form(f"edit_book_{selected_id}"):

                title = st.text_input(
                    "Title",
                    value=book["title"]
                )

                author = st.text_input(
                    "Author",
                    value=book["author"] or ""
                )

                description = st.text_area(
                    "Description",
                    value=book["description"] or ""
                )

                total = st.number_input(
                    "Total Copies",
                    min_value=0,
                    value=int(book["total_copies"]),
                    step=1
                )

                ebook_url = st.text_input(
                    "Reading URL",
                    value=book["ebook_url"] or ""
                )

                save = st.form_submit_button("Update Book")

                if save:

                    try:

                        success, message = update_book(
                            selected_id,
                            title,
                            author,
                            description,
                            int(total),
                            ebook_url
                        )

                        if success:
                            st.success(message)

                        else:
                            st.error(message)

                    except Exception as e:
                        st.error(f"Update failed: {e}")

            st.write(
                "Available Copies:",
                book["available_copies"]
            )

            if book["is_active"]:

                if st.button("Deactivate Book"):
                    set_book_active(selected_id, False)
                    st.rerun()

            else:

                if st.button("Reactivate Book"):
                    set_book_active(selected_id, True)
                    st.rerun()

        else:
            st.info("No books found.")

    # ----------------------------
    # 4. Manage Users
    # ----------------------------

    with users_tab:

        st.subheader("Registered Users")

        users = list_users()

        if users:

            user_map = {
                u["user_id"]: u
                for u in users
            }

            selected_user_id = st.selectbox(
                "Select Account",
                options=list(user_map.keys()),
                format_func=lambda x: (
                    f"{user_map[x]['full_name']} "
                    f"({user_map[x]['email']})"
                )
            )

            selected_user = user_map[selected_user_id]

            st.write("Role:", selected_user["role"])
            st.write("Active:", selected_user["is_active"])

            if selected_user["role"] == "user":

                if selected_user["is_active"]:

                    if st.button("Deactivate User"):
                        set_user_active(selected_user_id, False)
                        st.rerun()

                else:

                    if st.button("Activate User"):
                        set_user_active(selected_user_id, True)
                        st.rerun()

            else:
                st.info("Admin account management is restricted.")

            st.dataframe(
                users,
                use_container_width=True,
                hide_index=True
            )

    # ----------------------------
    # 5. Borrowing Records
    # ----------------------------

    with loans_tab:

        st.subheader("All Borrowing Records")

        loans = get_all_loans()

        if loans:

            st.dataframe(
                loans,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No borrowing records found.")
