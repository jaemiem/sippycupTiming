import streamlit as st
import pandas as pd
import csv

DATABASE = "rfid_database.csv"

def load_database():
    try:
        df = pd.read_csv(DATABASE)
        if df.empty:
            df = pd.DataFrame(columns=["RFID", "Driver Name", "Driver Number", "Driver Kart", "Driver Kart CC"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["RFID", "Driver Name", "Driver Number", "Driver Kart", "Driver Kart CC"])
    return df

def save_database(data):
    try:
        data.to_csv(DATABASE, index=False)
        st.success("Database saved successfully.")
    except Exception as e:
        st.error(f"Error saving to database: {e}")

def driver_setup_page(rfid_interface):
    st.title("Driver Setup")

    data = load_database()

    # Ensure the first row (header) is ignored
    data = data.reset_index(drop=True)
    if not data.empty and data.iloc[0].isnull().all():
        data = data.drop(data.index[0])

    detected_rfids = rfid_interface.get_detected_rfids()

    rfid_table = []
    for rfid in detected_rfids:
        details = data[data["RFID"] == rfid]
        if details.empty:
            details = {
                "Driver Name": "Not Assigned",
                "Driver Number": "Not Assigned",
                "Driver Kart": "Not Assigned",
                "Driver Kart CC": "Not Assigned"
            }
        else:
            details = details.iloc[0].to_dict()
        
        rfid_table.append({
            "RFID": rfid,
            "Driver Name": details["Driver Name"],
            "Driver Number": details["Driver Number"],
            "Driver Kart": details["Driver Kart"],
            "Driver Kart CC": details["Driver Kart CC"]
        })

    if rfid_table:
        for row in rfid_table:
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
                        data.loc[data["RFID"] == row["RFID"], ["Driver Name", "Driver Number", "Driver Kart", "Driver Kart CC"]] = [new_name, new_number, new_kart, new_kart_cc]
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
