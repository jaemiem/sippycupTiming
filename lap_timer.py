import pandas as pd
import streamlit as st
import time
import json
from ttl_interface import TTLInterface, SerialException

LAP_DATABASE = "lap_timer.csv"
SETTINGS_FILE = "settings.json"

def load_lap_database():
    try:
        df = pd.read_csv(LAP_DATABASE)
        if df.empty:
            df = pd.DataFrame(columns=["ID", "Lap Time", "Best Lap", "Last Lap"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["ID", "Lap Time", "Best Lap", "Last Lap"])
    return df

def save_lap_database(data):
    try:
        data.to_csv(LAP_DATABASE, index=False)
    except Exception as e:
        print(f"Error saving to lap database: {e}")

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{minutes:02}:{seconds:02}:{milliseconds:03}"

def update_lap_times(rfid):
    print(f"Updating lap times for RFID: {rfid}")
    df = load_lap_database()
    current_time = time.time()
    
    if rfid in df["ID"].values:
        driver_data = df[df["ID"] == rfid]
        last_lap_time = driver_data["Last Lap"].values[0]
        if last_lap_time != "Not Set":
            last_lap_time = float(last_lap_time)
            lap_time = current_time - last_lap_time
        else:
            lap_time = 0

        best_lap_time = driver_data["Best Lap"].values[0]
        if best_lap_time == "Not Set" or lap_time < float(best_lap_time):
            best_lap_time = lap_time

        df.loc[df["ID"] == rfid, ["Lap Time", "Best Lap", "Last Lap"]] = [format_time(lap_time), format_time(best_lap_time), current_time]
    else:
        new_entry = pd.DataFrame([{
            "ID": rfid,
            "Lap Time": "Not Set",
            "Best Lap": "Not Set",
            "Last Lap": current_time
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
    
    save_lap_database(df)

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {}
    return settings

def lap_detected(rfid):
    print(f"RFID detected: {rfid}")
    if st.session_state.get('race_started', False):
        update_lap_times(rfid)
    else:
        print("Race not started. Data not recorded.")

def init_ttl_interface():
    settings = load_settings()
    com_port = settings.get("selected_com_port")
    baud_rate = settings.get("baud_rate")
    
    if com_port and baud_rate:
        try:
            ttl_interface = TTLInterface(lap_detected, com_port, baud_rate)
            ttl_interface.start()
            st.session_state.ttl_interface = ttl_interface
            st.session_state.ttl_interface_active = True
            print(f"Initialized TTL Interface on {com_port} at {baud_rate} baud.")
        except SerialException as e:
            print(f"Failed to initialize TTL interface: {e}")
    else:
        print("COM port or baud rate not set in settings.")

def start_race():
    st.session_state.race_started = True
    print("Race started")

def stop_race():
    st.session_state.race_started = False
    print("Race stopped")

def lap_timer_page():
    st.title("Lap Timer")

    if 'race_started' not in st.session_state:
        st.session_state.race_started = False

    if st.session_state.race_started:
        if st.button("Stop Race"):
            stop_race()
            st.success("Race stopped.")
    else:
        if st.button("Start Race"):
            start_race()
            st.success("Race started.")

    if 'ttl_interface_active' in st.session_state and st.session_state.ttl_interface_active:
        st.markdown('<span style="color: green; font-size: 24px;">●</span> Connection Active', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color: red; font-size: 24px;">●</span> Connection Inactive', unsafe_allow_html=True)

    df = load_lap_database()
    if not df.empty:
        st.dataframe(df[["ID", "Lap Time", "Best Lap", "Last Lap"]])
    else:
        st.write("No lap times recorded yet.")

if __name__ == "__main__":
    init_ttl_interface()
    lap_timer_page()
