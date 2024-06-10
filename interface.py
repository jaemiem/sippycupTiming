import time
import threading
import random
import csv
import streamlit as st

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

class RFIDInterface:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.data = load_database()
        self.current_rfid = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.detect_rfid_signals)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def detect_rfid_signals(self):
        while self.running:
            # Simulate RFID signal reading
            time.sleep(3)  # Replace with actual signal detection logic
            rfid = f"{random.randint(230855203, 230865498):012d}"  # Simulated RFID
            self.current_rfid = rfid
            self.callback(rfid)

    def add_rfid(self, rfid):
        if rfid not in self.data:
            self.data[rfid] = {
                "Driver Name": "Not Assigned",
                "Driver Number": "Not Assigned",
                "Driver Kart": "Not Assigned",
                "Driver Kart CC": "Not Assigned"
            }
            save_database(self.data)

    def remove_rfid(self, rfid):
        if rfid in self.data:
            del self.data[rfid]
            save_database(self.data)

    def get_detected_rfids(self):
        return self.data.keys()

    # Method to simulate RFID detection for test purposes
    def simulate_rfid_detection(self):
        rfid = f"{random.randint(230855203, 230865498):012d}"  # Generate a random RFID
        self.current_rfid = rfid
        self.callback(rfid)

class TTLInterface:
    def __init__(self, callback):
        self.callback = callback
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_ttl_signals)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def read_ttl_signals(self):
        while self.running:
            # Simulate TTL signal reading
            time.sleep(1)  # Replace with actual signal detection logic
            signal = True  # This should be the actual signal read
            if signal:
                self.callback()
