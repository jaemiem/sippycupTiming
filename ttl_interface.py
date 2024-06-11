import time
import threading
import serial  # Assuming you're using the pyserial library
from serial import SerialException

class TTLInterface:
    def __init__(self, callback, com_port, baud_rate=9600):
        self.callback = callback
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.running = False
        self.serial_conn = None
        self.received_data = []

    def start(self):
        self.running = True
        try:
            self.serial_conn = serial.Serial(self.com_port, self.baud_rate, timeout=1)  # Set the appropriate baud rate
            self.thread = threading.Thread(target=self.read_ttl_signals)
            self.thread.start()
        except SerialException as e:
            raise SerialException(f"Failed to open COM port {self.com_port}: {e}")

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        if self.thread:
            self.thread.join()

    def read_ttl_signals(self):
        while self.running:
            try:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()  # Read a line of data
                    if line:  # If a line is read
                        self.received_data.append(line)
                        self.callback()
            except Exception as e:
                print(f"Error reading from COM port: {e}")

    def get_received_data(self):
        return self.received_data

    def is_active(self):
        return self.running
