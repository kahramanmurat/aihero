"""
Simple test to verify chat_input works
"""
import streamlit as st

st.title("Chat Input Test")
st.write("If you can see a chat input box at the bottom, it's working!")

prompt = st.chat_input("Type something here...")
if prompt:
    st.write(f"You typed: {prompt}")

