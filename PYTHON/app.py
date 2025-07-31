# Make sure to install pyserial: pip install pyserial

import serial
import csv
import time
from datetime import datetime
import os

def get_serial_port():
    port = input("Enter the serial port (e.g., COM3 or /dev/ttyACM0): ").strip()
    return port

def get_csv_filename():
    use_new = input("Create a new CSV file? (y/n): ").strip().lower()
    if use_new == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_data_{timestamp}.csv"
        print(f"New file will be created: {filename}")
        return filename
    else:
        return "sensor_data.csv"

def main():
    SERIAL_PORT = get_serial_port()
    CSV_FILE = get_csv_filename()
    BAUD_RATE = 9600  # Match this to your Arduino's Serial.begin() baud rate

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    o2 = None
    co2 = None

    # Open CSV and write header if needed
    with open(CSV_FILE, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:
            writer.writerow(['timestamp', 'O2', 'CO2'])

        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue

                if line.startswith('O2:'):
                    try:
                        o2 = float(line.split(':')[1])
                    except ValueError:
                        o2 = None
                elif line.startswith('CO2:'):
                    try:
                        co2 = int(float(line.split(':')[1]))
                    except ValueError:
                        co2 = None

                # Write to CSV only when both values are available
                if o2 is not None and co2 is not None:
                    timestamp = datetime.now().isoformat()
                    writer.writerow([timestamp, o2, co2])
                    csvfile.flush()
                    print(f"{timestamp} | O2: {o2} | CO2: {co2}")
                    o2 = None
                    co2 = None

            except KeyboardInterrupt:
                print("Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()