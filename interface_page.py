import streamlit as st
import pandas as pd
import serial.tools.list_ports  # To list available COM ports
from serial import SerialException  # To handle serial exceptions
from rfid_generator import RFIDInterface  # Updated import
from ttl_interface import TTLInterface  # Import from the new module
from driver_setup import load_database
from lap_timer import lap_detected  # Import lap_detected function
import time

# Function to initialize the TTL interface
def init_ttl_interface(selected_com_port):
    try:
        st.session_state.ttl_interface = TTLInterface(lap_detected, selected_com_port)
        st.session_state.ttl_interface.start()
        st.session_state.ttl_interface_active = True
        st.success(f"Monitoring TTL on {selected_com_port}")
    except SerialException as e:
        st.error(f"Failed to open COM port {selected_com_port}: {e}")

# Function to stop the TTL interface
def stop_ttl_interface():
    if 'ttl_interface_active' in st.session_state and st.session_state.ttl_interface_active:
        st.session_state.ttl_interface.stop()
        st.session_state.ttl_interface_active = False
        st.success("Stopped TTL monitoring")

# Function to restart the TTL interface
def restart_ttl_interface():
    stop_ttl_interface()
    if 'selected_com_port' in st.session_state:
        init_ttl_interface(st.session_state.selected_com_port)

# Streamlit page definition
def interface_page():
    st.title("Interface")
    input_mode = st.selectbox("Select Input Mode", ["TTL", "RFID Test"])

    if input_mode == "TTL":
        # List available COM ports
        ports = serial.tools.list_ports.comports()
        com_ports = [port.device for port in ports]
        
        if com_ports:
            selected_com_port = st.selectbox("Select COM Port", com_ports)

            if st.button("Apply Settings"):
                st.session_state.selected_com_port = selected_com_port
                restart_ttl_interface()
                st.success(f"Settings applied for COM port: {selected_com_port}")

            if st.button("Restart TTL Service"):
                restart_ttl_interface()
        else:
            st.write("No COM ports available. Please connect a device.")
    
    if input_mode == "RFID Test":
        if st.button("Generate Mock RFID"):
            st.session_state.rfid_interface.simulate_rfid_detection()
            st.success(f"Mock RFID generated. Please add it to the database if needed.")

    st.header("Listen for RFID")
    listening = st.checkbox("Listen for RFID")
    st.session_state.listening = listening

    if 'detected_ids' not in st.session_state:
        st.session_state.detected_ids = set()

    if 'ttl_interface_active' not in st.session_state:
        st.session_state.ttl_interface_active = False

    if 'captured_log' not in st.session_state:
        st.session_state.captured_log = []

    if st.session_state.listening:
        data_display = st.empty()
        if input_mode == "TTL" and 'selected_com_port' in st.session_state:
            if not st.session_state.ttl_interface_active:
                init_ttl_interface(st.session_state.selected_com_port)
            while st.session_state.listening:
                received_data = st.session_state.ttl_interface.get_received_data()
                if received_data:
                    new_data = []
                    for data in received_data:
                        if data not in st.session_state.detected_ids:
                            st.session_state.detected_ids.add(data)
                            new_data.append(data)
                            # Add to log
                            st.session_state.captured_log.append(data)
                    if new_data:
                        data_display.write("Received Data:")
                        data_display.code('\n'.join(st.session_state.captured_log))
                time.sleep(0.5)

        elif input_mode == "RFID Test":
            while st.session_state.listening:
                if st.session_state.rfid_interface.current_rfid:
                    if st.session_state.rfid_interface.current_rfid not in st.session_state.detected_ids:
                        st.session_state.detected_ids.add(st.session_state.rfid_interface.current_rfid)
                        # Add to log
                        st.session_state.captured_log.append(st.session_state.rfid_interface.current_rfid)
                        data_display.write(f"Detected RFID: {st.session_state.rfid_interface.current_rfid}")
                        if st.button("Add Detected RFID to Database"):
                            st.session_state.rfid_interface.add_rfid(st.session_state.rfid_interface.current_rfid)
                            st.success(f"RFID {st.session_state.rfid_interface.current_rfid} added to the database.")
                            st.session_state.mock_rfid = None
                time.sleep(0.5)

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

# Ensure RFIDInterface and TTLInterface classes are properly defined and imported
# Ensure the lap_detected function is properly defined and imported

# Entry point to the Streamlit app
if __name__ == "__main__":
    interface_page()
