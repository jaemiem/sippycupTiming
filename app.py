# app.py
import subprocess
import sys
import streamlit as st
from streamlit_option_menu import option_menu
from dashboard import dashboard_page
from driver_setup import driver_setup_page
from interface_page import interface_page
from terminal_page import terminal_page
from rfid_generator import RFIDInterface  # Updated import
from ttl_interface import TTLInterface  # Import from the new module

# Function to install packages
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of required packages
required_packages = [
    "streamlit",
    "streamlit_option_menu",
]

# Try to import required packages, install if not available
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

# Redirect standard output and standard error to the log capturer
from log_capturer import log_capturer
sys.stdout = log_capturer
sys.stderr = log_capturer

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
        ["Dashboard", "Driver Setup", "Interface", "Terminal"],
        icons=["house", "gear", "antenna", "terminal"],
        menu_icon="cast",
        default_index=0,
    )

# Page routing
if page == "Dashboard":
    dashboard_page()
elif page == "Driver Setup":
    driver_setup_page(st.session_state.rfid_interface)
elif page == "Interface":
    interface_page()
elif page == "Terminal":
    terminal_page()
