import streamlit as st
import pandas as pd
import serial.tools.list_ports  # To list available COM ports
from serial import SerialException  # To handle serial exceptions
from ttl_interface import TTLInterface  # Import from the new module
from lap_timer import lap_detected  # Import lap_detected function
import json
import time
import psutil  # To handle process management on Windows
import subprocess  # To run system commands

# File to store settings
SETTINGS_FILE = "settings.json"
DATABASE_FILE = "rfid_database.csv"

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_database():
    try:
        df = pd.read_csv(DATABASE_FILE)
        if df.empty:
            df = pd.DataFrame(columns=["RFID", "Driver Name", "Driver Number", "Driver Kart", "Driver Kart CC"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["RFID", "Driver Name", "Driver Number", "Driver Kart", "Driver Kart CC"])
    return df

def save_to_database(rfid):
    df = load_database()
    if rfid not in df["RFID"].values:
        new_entry = pd.DataFrame([{
            "RFID": rfid,
            "Driver Name": "Not Assigned",
            "Driver Number": "Not Assigned",
            "Driver Kart": "Not Assigned",
            "Driver Kart CC": "Not Assigned"
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DATABASE_FILE, index=False)  # Ensure the header is written correctly
        st.success(f"RFID {rfid} added to the database with default details.")
    else:
        st.warning(f"RFID {rfid} is already in the database.")


# Function to initialize the TTL interface
def init_ttl_interface(selected_com_port, baud_rate):
    try:
        st.session_state.ttl_interface = TTLInterface(lap_detected, selected_com_port, baud_rate)
        st.session_state.ttl_interface.start()
        st.session_state.ttl_interface_active = True
        st.success(f"Monitoring TTL on {selected_com_port} at {baud_rate} baud")
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
    if 'selected_com_port' in st.session_state and 'baud_rate' in st.session_state:
        init_ttl_interface(st.session_state.selected_com_port, st.session_state.baud_rate)

# Function to test the TTL interface connection
def test_ttl_interface(selected_com_port, baud_rate):
    try:
        with serial.Serial(selected_com_port, baud_rate, timeout=1) as ser:
            ser.write(b'')  # Sending an empty byte to test connection
            ser.read()  # Trying to read (even though it will timeout)
        st.success(f"Successfully connected to {selected_com_port} at {baud_rate} baud")
    except SerialException as e:
        st.error(f"Failed to connect to {selected_com_port}: {e}")

# Function to find the process using the COM port
def find_process_using_com_port(port):
    try:
        # Running the handle command from Sysinternals to find the process using the COM port
        result = subprocess.run(['handle', port], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if port in line:
                    st.write(line)
                    pid = int(line.split()[-1].strip())
                    return pid
        return None
    except Exception as e:
        st.error(f"Error finding process using COM port: {e}")
        return None

# Function to terminate the process using the COM port
def terminate_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=3)
        st.success(f"Terminated process {pid} using the COM port.")
    except Exception as e:
        st.error(f"Failed to terminate process {pid}: {e}")

# Streamlit page definition
def interface_page():
    st.title("Interface")
    
    settings = load_settings()
    
    input_mode = "TTL"  # Fixed to TTL as RFID Test module is removed

    # List available COM ports
    ports = serial.tools.list_ports.comports()
    com_ports = [port.device for port in ports]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_com_port = st.selectbox("Select COM Port", com_ports, index=settings.get("selected_com_port_index", 0))
    with col2:
        baud_rate = st.selectbox("Select Baud Rate", [9600, 19200, 38400, 57600, 115200], index=settings.get("baud_rate_index", 0))

    # Save settings when "Apply Settings" is clicked
    if st.button("Apply Settings", key="ttl_apply_settings"):
        st.session_state.selected_com_port = selected_com_port
        st.session_state.baud_rate = baud_rate
        settings["selected_com_port"] = selected_com_port
        settings["baud_rate"] = baud_rate
        settings["selected_com_port_index"] = com_ports.index(selected_com_port)
        settings["baud_rate_index"] = [9600, 19200, 38400, 57600, 115200].index(baud_rate)
        save_settings(settings)
        st.success(f"Settings saved for COM port: {selected_com_port} at {baud_rate} baud")

    if not com_ports:
        st.write("No COM ports available. Please connect a device.")

    col3, col4 = st.columns([1, 1])
    with col3:
        if st.button("Test Connection", key="test_connection"):
            test_ttl_interface(selected_com_port, baud_rate)
    with col4:
        if st.button("Force Close Port", key="force_close"):
            pid = find_process_using_com_port(selected_com_port)
            if pid:
                terminate_process(pid)
            else:
                st.write("No process found using the COM port.")
    
    st.header("Listen for RFID")
    listening = st.toggle("Listen for RFID", value=settings.get("auto_listen", False))
    if listening:
        st.session_state.listening = True
        settings["auto_listen"] = True
        save_settings(settings)
        # Automatically apply saved settings when starting to listen
        if 'selected_com_port' not in st.session_state or 'baud_rate' not in st.session_state:
            st.session_state.selected_com_port = settings.get("selected_com_port")
            st.session_state.baud_rate = settings.get("baud_rate")
        if not st.session_state.ttl_interface_active:
            init_ttl_interface(st.session_state.selected_com_port, st.session_state.baud_rate)
    else:
        if 'listening' in st.session_state and st.session_state.listening:
            stop_ttl_interface()
        st.session_state.listening = False
        settings["auto_listen"] = False
        save_settings(settings)

    if 'detected_ids' not in st.session_state:
        st.session_state.detected_ids = set()

    if 'ttl_interface' not in st.session_state:
        st.session_state.ttl_interface = None

    if 'ttl_interface_active' not in st.session_state:
        st.session_state.ttl_interface_active = False

    if 'captured_log' not in st.session_state:
        st.session_state.captured_log = []

    # Display the detected codes in rows with add button
    if st.session_state.listening:
        if 'selected_com_port' in st.session_state:
            if not st.session_state.ttl_interface_active:
                init_ttl_interface(st.session_state.selected_com_port, st.session_state.baud_rate)
            while st.session_state.listening:
                received_data = st.session_state.ttl_interface.get_received_data()
                if received_data:
                    for data in received_data:
                        if data not in st.session_state.detected_ids:
                            st.session_state.detected_ids.add(data)
                            st.session_state.captured_log.append(data)
                            cols = st.columns([2, 2, 1])
                            with cols[0]:
                                st.write("Detected ID:")
                            with cols[1]:
                                st.write(data)
                            with cols[2]:
                                if st.button(f"Add to Database", key=f"add_{data}"):
                                    save_to_database(data)
                time.sleep(0.5)
    else:
        for data in st.session_state.captured_log:
            cols = st.columns([2, 2, 1])
            with cols[0]:
                st.write("Detected ID:")
            with cols[1]:
                st.write(data)
            with cols[2]:
                if st.button(f"Add to Database", key=f"add_{data}_off"):
                    save_to_database(data)

if __name__ == "__main__":
    interface_page()
