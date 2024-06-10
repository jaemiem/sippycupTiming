# lap_timer.py
import time
import csv

LAP_LOG = "lap_times.csv"
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
        log_lap_time(lap_duration)
        return lap_duration
    return None

def log_lap_time(lap_duration):
    with open(LAP_LOG, mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([lap_duration])

def get_all_lap_times():
    return lap_times

def reset_lap_times():
    global lap_times, start_time
    lap_times = []
    start_time = None
