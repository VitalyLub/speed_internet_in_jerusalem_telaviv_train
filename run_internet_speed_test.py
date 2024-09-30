import subprocess
import csv
import time
import re

def measure_speed():
    try:
        result = subprocess.run(['speedtest'], capture_output=True, text=True)
        output = result.stdout
        print(output)
        
        # Use regex to extract download and upload speeds from the text
        download_speed = re.search(r'Download:\s+(\d+\.\d+)\s+Mbit/s', output)
        upload_speed = re.search(r'Upload:\s+(\d+\.\d+)\s+Mbit/s', output)
        
        if download_speed and upload_speed:
            return float(download_speed.group(1)), float(upload_speed.group(1))
        else:
            print("Error: Could not find speed results in the output.")
            return None, None
    
    except Exception as e:
        print(f"Error running speedtest: {e}")
        return None, None

def append_to_csv(filename, timestamp1, timestamp2, download_speed, upload_speed):
    # Append a row to the CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write the data row
        writer.writerow([timestamp1, timestamp2, download_speed, upload_speed])

def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def main():
    create_time = get_current_time().replace(':', '-')
    filename = f'/Users/vitaly_lubimzev/Desktop/internet_speed_log_test_{create_time}.csv'

    # Write the headers once, if the file doesn't exist or is empty
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Start Time', 'End Time', 'Download Speed (Mbit/s)', 'Upload Speed (Mbit/s)'])

    while True:
        start_time = get_current_time()
        print(f"Start time: {start_time}")
        download_speed, upload_speed = measure_speed()
        if download_speed is not None and upload_speed is not None:
            end_time = get_current_time()
            print(f"Start time: {start_time} - End time: {end_time} - Download: {download_speed} Mbit/s, Upload: {upload_speed} Mbit/s")
            
            append_to_csv(filename, start_time, end_time, download_speed, upload_speed)
        else:
            end_time = get_current_time()
            download_speed, upload_speed = 0, 0
            append_to_csv(filename, start_time, end_time, download_speed, upload_speed)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
