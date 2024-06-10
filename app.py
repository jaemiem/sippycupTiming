import serial
import time
import csv

# Constants
SERIAL_PORT = '/dev/ttyUSB0'  # Update this with your serial port
BAUD_RATE = 9600
LAP_LOG = "lap_times.csv"

# Setup
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
lap_times = []
start_time = None

def lap_detected():
    global start_time
    lap_time = time.time()
    if start_time is None:
        start_time = lap_time
    else:
        lap_duration = lap_time - start_time
        lap_times.append(lap_duration)
        start_time = lap_time
        print(f"Lap detected: {lap_duration:.2f} seconds")

        # Save lap times to a CSV file
        with open(LAP_LOG, mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([lap_duration])

try:
    print("Lap timer started. Press Ctrl+C to stop.")
    while True:
        if ser.in_waiting > 0:
            signal = ser.readline().decode().strip()
            if signal == '1':  # Assuming '1' indicates a lap detection
                lap_detected()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopping lap timer.")
finally:
    ser.close()

# Print all lap times
print("All lap times:")
for lap in lap_times:
    print(f"{lap:.2f} seconds")
