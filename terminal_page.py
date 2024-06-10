import streamlit as st
from log_capturer import log_capturer

def terminal_page():
    st.title("Terminal Output in Streamlit")

    if st.button("Refresh"):
        log_contents = log_capturer.get_log_contents()
    
        if log_contents:
            st.subheader("Output")
            st.code("\n".join(log_contents))
        else:
            st.write("No output yet.")
