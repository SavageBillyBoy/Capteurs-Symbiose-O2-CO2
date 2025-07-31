# Make sure to install pyserial: pip install pyserial

import serial
import csv
import time
from datetime import datetime
import os
import serial.tools.list_ports

def find_sensor_port(baudrate=9600, timeout=2):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate, timeout=1)
            found_o2 = False
            found_co2 = False
            start_time = time.time()
            while time.time() - start_time < timeout:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('O2:'):
                    found_o2 = True
                elif line.startswith('CO2:'):
                    found_co2 = True
                if found_o2 and found_co2:
                    ser.close()
                    print(f"Auto-selected port: {port.device}")
                    return port.device
            ser.close()
        except Exception:
            continue
    print("No suitable serial port found with O2 and CO2 data.")
    exit(1)

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
    BAUD_RATE = 9600  # Match this to your Arduino's Serial.begin() baud rate
    SERIAL_PORT = find_sensor_port(baudrate=BAUD_RATE)
    CSV_FILE = get_csv_filename()

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