import streamlit as st
import pandas as pd
from interface import TTLInterface, RFIDInterface
from driver_setup import load_database

def interface_page():
    st.title("Interface")
    input_mode = st.selectbox("Select Input Mode", ["TTL", "RFID Test"])

    def start_interface():
        if input_mode == "TTL":
            st.session_state.interface = TTLInterface(lambda: st.write("TTL signal detected"))
            st.session_state.interface.start()
        elif input_mode == "RFID Test":
            st.session_state.interface = None

    def stop_interface():
        if st.session_state.interface:
            st.session_state.interface.stop()
        st.session_state.rfid_interface.stop()
        st.session_state.listening = False

    def generate_mock_rfid():
        st.session_state.rfid_interface.simulate_rfid_detection()
        st.success(f"Mock RFID generated. Please add it to the database if needed.")

    if input_mode != "RFID Test":
        start_interface()
    
    if input_mode == "RFID Test":
        if st.button("Generate Mock RFID"):
            generate_mock_rfid()

    st.header("Listen for RFID")
    listening = st.toggle("Listen for RFID")
    st.session_state.listening = listening

    if st.session_state.listening:
        if st.session_state.rfid_interface.current_rfid:
            st.write(f"Detected RFID: {st.session_state.rfid_interface.current_rfid}")
            if st.button("Add Detected RFID to Database"):
                st.session_state.rfid_interface.add_rfid(st.session_state.rfid_interface.current_rfid)
                st.success(f"RFID {st.session_state.rfid_interface.current_rfid} added to the database.")
                st.session_state.mock_rfid = None

    st.header("RFID Database")
    data = load_database()
    rfids = st.session_state.rfid_interface.get_detected_rfids()

    rfid_table = []
    for rfid in rfids:
        name = data.get(rfid, {}).get("Driver Name", "Not Assigned")
        rfid_table.append({
            "RFID": rfid,
            "Driver Name": name
        })

    if rfid_table:
        # Read the CSS file
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        st.write("RFID Database:")
        st.write("""
            <table class="rfid-table">
                <thead>
                    <tr>
                        <th>RFID</th>
                        <th>Driver Name</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)

        for entry in rfid_table:
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                st.write(entry["RFID"])
            with col2:
                st.write(entry["Driver Name"])
            with col3:
                if st.button("Delete", key=f"delete_{entry['RFID']}"):
                    st.session_state.rfid_interface.remove_rfid(entry["RFID"])
                    st.experimental_rerun()

        st.write("""
                </tbody>
            </table>
        """, unsafe_allow_html=True)
    else:
        st.write("No RFIDs detected.")
