import streamlit as st  
import openai

openai.api_key = "insert key here"


with st.sidebar:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for sender, message in st.session_state.messages:
        with st.chat_message(sender):
            st.write(message)

    if prompt := st.chat_input("Say something"):
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            reply = f"Error: {str(e)}"

        st.session_state.messages.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.write(reply)
