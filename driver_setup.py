import streamlit as st
import csv

DRIVER_DB = "drivers.csv"

def load_drivers():
    drivers = {}
    try:
        with open(DRIVER_DB, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                drivers[row[0]] = row[1]
    except FileNotFoundError:
        pass
    return drivers

def save_drivers(drivers):
    with open(DRIVER_DB, mode='w', newline='') as file:
        writer = csv.writer(file)
        for rfid, name in drivers.items():
            writer.writerow([rfid, name])

def driver_setup_page(rfid_interface):
    st.title("Driver Setup")

    drivers = load_drivers()
    st.write("Current Drivers:")
    for rfid, name in drivers.items():
        st.write(f"RFID: {rfid} - Name: {name}")

    detected_rfids = rfid_interface.get_detected_rfids()
    st.write("Detected RFIDs:")
    for rfid in detected_rfids:
        st.write(f"RFID: {rfid}")

    with st.form("driver_form"):
        rfid = st.selectbox("RFID", list(detected_rfids))
        name = st.text_input("Driver Name")
        submitted = st.form_submit_button("Add/Update Driver")
        if submitted:
            drivers[rfid] = name
            save_drivers(drivers)
            st.success(f"Driver {name} with RFID {rfid} has been added/updated.")
