import streamlit as st
from streamlit_option_menu import option_menu
from dashboard import dashboard_page
from driver_setup import driver_setup_page
from interface_page import interface_page
from interface import RFIDInterface

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# State initialization
if 'interface' not in st.session_state:
    st.session_state.interface = None

if 'rfid_interface' not in st.session_state:
    st.session_state.rfid_interface = RFIDInterface(lambda rfid: st.write(f"RFID detected: {rfid}"))

if 'listening' not in st.session_state:
    st.session_state.listening = False

if 'mock_rfid' not in st.session_state:
    st.session_state.mock_rfid = None

# Page navigation
with st.sidebar:
    page = option_menu(
        "Navigation",
        ["Dashboard", "Driver Setup", "Interface"],
        icons=["house", "gear", "antenna"],  # optional icons from https://icons.getbootstrap.com/
        menu_icon="cast",  # optional
        default_index=0,  # default selected item
    )

# Page routing
if page == "Dashboard":
    dashboard_page()
elif page == "Driver Setup":
    driver_setup_page(st.session_state.rfid_interface)
elif page == "Interface":
    interface_page()
