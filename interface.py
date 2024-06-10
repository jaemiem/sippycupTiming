import time
import threading
import random
import csv

RFID_DB = "rfid_db.csv"

def load_rfids():
    rfids = set()
    try:
        with open(RFID_DB, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                rfids.add(row[0])
    except FileNotFoundError:
        pass
    return rfids

def save_rfid(rfid):
    with open(RFID_DB, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([rfid])

def remove_rfid(rfid):
    rfids = load_rfids()
    if rfid in rfids:
        rfids.remove(rfid)
        with open(RFID_DB, mode='w', newline='') as file:
            writer = csv.writer(file)
            for r in rfids:
                writer.writerow([r])

class RFIDInterface:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.detected_rfids = load_rfids()
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
            rfid = f"{random.randint(1000000000, 9999999999)}"  # Simulated RFID
            self.current_rfid = rfid
            self.callback(rfid)

    def add_rfid(self, rfid):
        if rfid not in self.detected_rfids:
            self.detected_rfids.add(rfid)
            save_rfid(rfid)

    def remove_rfid(self, rfid):
        if rfid in self.detected_rfids:
            self.detected_rfids.remove(rfid)
            remove_rfid(rfid)

    def get_detected_rfids(self):
        return self.detected_rfids

    # Method to simulate RFID detection for test purposes
    def simulate_rfid_detection(self, rfid):
        if rfid not in self.detected_rfids:
            self.detected_rfids.add(rfid)
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

class SerialInterface:
    def __init__(self, callback):
        self.callback = callback
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_serial_signals)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def read_serial_signals(self):
        while self.running:
            # Simulate Serial signal reading
            time.sleep(2)  # Replace with actual signal detection logic
            signal = True  # This should be the actual signal read
            if signal:
                self.callback()
