# driver_setup.py
import streamlit as st
import pandas as pd
import csv

DATABASE = "rfid_database.csv"

def load_database():
    data = {}
    try:
        with open(DATABASE, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                rfid = row[0]
                data[rfid] = {
                    "Driver Name": row[1],
                    "Driver Number": row[2],
                    "Driver Kart": row[3],
                    "Driver Kart CC": row[4]
                }
    except FileNotFoundError:
        st.error("Database file not found.")
    except Exception as e:
        st.error(f"Error reading database: {e}")
    return data

def save_database(data):
    try:
        with open(DATABASE, mode='w', newline='') as file:
            writer = csv.writer(file)
            for rfid, details in data.items():
                writer.writerow([rfid, details["Driver Name"], details["Driver Number"], details["Driver Kart"], details["Driver Kart CC"]])
    except Exception as e:
        st.error(f"Error saving to database: {e}")

def driver_setup_page(rfid_interface):
    st.title("Driver Setup")

    data = load_database()
    detected_rfids = rfid_interface.get_detected_rfids()

    rfid_table = []
    for rfid in detected_rfids:
        details = data.get(rfid, {
            "Driver Name": "Not Assigned",
            "Driver Number": "Not Assigned",
            "Driver Kart": "Not Assigned",
            "Driver Kart CC": "Not Assigned"
        })
        rfid_table.append({
            "RFID": rfid,
            "Driver Name": details["Driver Name"],
            "Driver Number": details["Driver Number"],
            "Driver Kart": details["Driver Kart"],
            "Driver Kart CC": details["Driver Kart CC"]
        })

    if rfid_table:
        df = pd.DataFrame(rfid_table)

        st.write("RFID Database:")
        st.table(df)

        for index, row in df.iterrows():
            if st.session_state.get(f'edit_{row["RFID"]}', False):
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                with col1:
                    st.write(row["RFID"])
                with col2:
                    new_name = st.text_input("Driver Name", value=row["Driver Name"], key=f"name_{row['RFID']}")
                with col3:
                    new_number = st.text_input("Driver Number", value=row["Driver Number"], key=f"number_{row['RFID']}")
                with col4:
                    new_kart = st.selectbox("Driver Kart", ["Kart 1", "Kart 2", "Kart 3"], key=f"kart_{row['RFID']}")
                with col5:
                    new_kart_cc = st.selectbox("Driver Kart CC", ["100cc", "125cc", "150cc"], key=f"kart_cc_{row['RFID']}")
                with col6:
                    if st.button("Save", key=f"save_{row['RFID']}"):
                        data[row["RFID"]] = {
                            "Driver Name": new_name,
                            "Driver Number": new_number,
                            "Driver Kart": new_kart,
                            "Driver Kart CC": new_kart_cc
                        }
                        save_database(data)
                        st.success(f"Driver {new_name} with RFID {row['RFID']} updated.")
                        st.session_state[f'edit_{row["RFID"]}'] = False
                        st.experimental_rerun()
                    if st.button("Cancel", key=f"cancel_{row['RFID']}"):
                        st.session_state[f'edit_{row["RFID"]}'] = False
            else:
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                with col1:
                    st.write(row["RFID"])
                with col2:
                    st.write(row["Driver Name"])
                with col3:
                    st.write(row["Driver Number"])
                with col4:
                    st.write(row["Driver Kart"])
                with col5:
                    st.write(row["Driver Kart CC"])
                with col6:
                    if st.button("Edit", key=f"edit_{row['RFID']}"):
                        st.session_state[f'edit_{row["RFID"]}'] = True
    else:
        st.write("No RFIDs detected.")
