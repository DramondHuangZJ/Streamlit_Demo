"""A small, data-free app for testing GitHub-to-Streamlit deployment."""

import streamlit as st

DEMO_VERSION = "connection-demo-v1"

st.set_page_config(page_title="Streamlit Connection Demo", page_icon="🔗", layout="centered")

st.caption("DEPLOYMENT TEST")
st.title("Your Streamlit demo is running")
st.write("A simple check before building the PhD board-game pilot website.")
st.code(DEMO_VERSION, language=None)
st.info("Seeing this page confirms the demo app is running. The version above identifies the code being served.")

with st.container(border=True):
    st.subheader("Try an interaction")
    st.write("Click the button to check that the app responds and keeps its count across reruns.")
    if "demo_clicks" not in st.session_state:
        st.session_state.demo_clicks = 0
    if st.button("Test the connection", type="primary"):
        st.session_state.demo_clicks += 1
    st.metric("Successful clicks this session", st.session_state.demo_clicks)
    if st.session_state.demo_clicks:
        st.success("Interaction successful. Your demo is responding.")

st.link_button("View the GitHub repository", "https://github.com/DramondHuangZJ/Streamlit_Demo")
st.caption("Connection test only. No questionnaire, email delivery, or participant data collection. The click count resets when the session ends.")
