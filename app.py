import streamlit as st
import random  # Import the random module
import csv
import pandas as pd
import lap_timer
from interface import TTLInterface, SerialInterface, RFIDInterface
from driver_setup import driver_setup_page, load_drivers

# State initialization
if 'lap_times' not in st.session_state:
    st.session_state.lap_times = []

if 'interface' not in st.session_state:
    st.session_state.interface = None

if 'rfid_interface' not in st.session_state:
    st.session_state.rfid_interface = RFIDInterface(lambda rfid: st.write(f"RFID detected: {rfid}"))

# Page navigation
page = st.sidebar.selectbox("Select Page", ["Dashboard", "Driver Setup", "Interface"])

# Dashboard page
if page == "Dashboard":
    st.title("Dashboard")
    if st.session_state.lap_times:
        st.write("All lap times:")
        for lap in st.session_state.lap_times:
            if lap is not None:
                st.write(f"{lap:.2f} seconds")
    else:
        st.write("No lap times recorded yet.")

# Driver Setup page
elif page == "Driver Setup":
    driver_setup_page(st.session_state.rfid_interface)

# Interface page
elif page == "Interface":
    st.title("Interface")
    input_mode = st.selectbox("Select Input Mode", ["TTL", "Serial", "RFID Test"])

    def start_interface():
        if input_mode == "TTL":
            st.session_state.interface = TTLInterface(lap_timer.lap_detected)
            st.session_state.interface.start()
        elif input_mode == "Serial":
            st.session_state.interface = SerialInterface(lap_timer.lap_detected)
            st.session_state.interface.start()
        elif input_mode == "RFID Test":
            st.session_state.interface = None

    def generate_mock_rfid():
        mock_rfid = f"MOCK-{random.randint(1000, 9999)}"
        st.session_state.rfid_interface.simulate_rfid_detection(mock_rfid)
        st.success(f"Mock RFID {mock_rfid} generated and added to the detected list.")

    if input_mode != "RFID Test":
        start_interface()
    
    if input_mode == "RFID Test":
        if st.button("Generate Mock RFID"):
            generate_mock_rfid()

    st.header("RFID Database")
    drivers = load_drivers()
    rfids = st.session_state.rfid_interface.get_detected_rfids()

    rfid_table = []
    for rfid in rfids:
        name = drivers.get(rfid, "Not Assigned")
        rfid_table.append({"RFID": rfid, "Driver Name": name})

    st.write(pd.DataFrame(rfid_table))

    st.header("Listen for RFID")
    if st.button("Listen for RFID"):
        st.session_state.rfid_interface.start()
    
    if st.session_state.rfid_interface.current_rfid:
        st.write(f"Detected RFID: {st.session_state.rfid_interface.current_rfid}")
        if st.button("Add Detected RFID to Database"):
            st.session_state.rfid_interface.add_rfid(st.session_state.rfid_interface.current_rfid)
            st.success(f"RFID {st.session_state.rfid_interface.current_rfid} added to the database.")
    
    st.header("Remove RFID from Database")
    rfid_to_remove = st.selectbox("Select RFID to Remove", list(rfids))
    if st.button("Remove RFID"):
        st.session_state.rfid_interface.remove_rfid(rfid_to_remove)
        st.success(f"RFID {rfid_to_remove} removed from the database.")
