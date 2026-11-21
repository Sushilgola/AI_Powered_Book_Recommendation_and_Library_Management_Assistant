
# services/groq_service.py

import streamlit as st
from groq import Groq


@st.cache_resource
def get_groq_client():

    return Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )


def get_ai_response(chat_history):

    client = get_groq_client()

    system_message = {
        "role": "system",
        "content": """
        You are an AI Book Recommendation Assistant.

        Help users with:
        - Book recommendations
        - Book summaries
        - Author information
        - Reading suggestions

        Give simple, clear and concise responses.
        """
    }

    completion = client.chat.completions.create(

        model=st.secrets["GROQ_MODEL"],

        messages=[
            system_message,
            *chat_history[-12:]
        ],

        temperature=0.4,
        max_completion_tokens=600
    )

    return completion.choices[0].message.content
