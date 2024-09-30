import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
import datetime
import csv


def find_photos(directory_path):
    supported_formats = {'.jpg', '.jpeg', '.png', '.gif'}
    photo_files = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_formats):
                photo_files.append(os.path.join(root, file))

    return photo_files



def dms_to_decimal(lat_ref, lat_dms, lon_ref, lon_dms):
    decimal_latitude = lat_dms[0] + lat_dms[1] / 60 + lat_dms[2] / 3600
    if lat_ref == 'S':
        decimal_latitude = -decimal_latitude

    # Convert longitude
    decimal_longitude = lon_dms[0] + lon_dms[1] / 60 + lon_dms[2] / 3600
    if lon_ref == 'W':
        decimal_longitude = -decimal_longitude

    return float(decimal_latitude), float(decimal_longitude)

def extract_metadata_from_images(image_paths):
    metadata_list = []

    for image_path in image_paths:
        datetime_taken, latitude, longitude = extract_image_metadata(image_path)
        metadata_list.append({
            'image_path': image_path,
            'datetime_taken': datetime_taken,
            'latitude': latitude,
            'longitude': longitude
        })
    
    return metadata_list


def extract_image_metadata(image_path):
    # Open the image file
    img = Image.open(image_path)
    # Extract EXIF data
    info = img._getexif()
    
    if info is not None:
        # Extract date and time when the picture was taken
        datetime_taken = None
        gps_info = None

        for tag, value in info.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'DateTimeOriginal':
                datetime_taken = value  # Date and time the picture was taken

            # GPS info is nested under 'GPSInfo' tag
            if tag_name == 'GPSInfo':
                gps_info = {}
                for gps_tag, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = gps_value

        if gps_info:
            latitude, longitude = None, None
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info and 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                latitude, longitude = dms_to_decimal(gps_info['GPSLatitudeRef'], gps_info['GPSLatitude'], gps_info['GPSLongitudeRef'], gps_info['GPSLongitude'])
            
            return datetime_taken, latitude, longitude
        else:
            return datetime_taken, None, None



def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['datetime_taken', 'latitude', 'longitude'])
        # Write each list (row) to the CSV
        for row in data:
            writer.writerow(row)

def main():
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    photos = find_photos(input_dir)
    data = []

    for photo in photos:
        print(photo)
        datetime_taken, latitude, longitude = extract_image_metadata(photo)
        if datetime_taken and latitude and longitude:
            data.append([datetime_taken, latitude, longitude])
    save_to_csv(data, f'{output_dir}internet_speed_log_test_time_lat_lon.csv')


if __name__ == "__main__":
    main()
