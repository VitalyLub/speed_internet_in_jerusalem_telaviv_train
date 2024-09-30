import sys
import pandas as pd
import numpy as np
import folium
import matplotlib


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1.csv> <file2.csv>")
        sys.exit(1)

    # Get the file paths from the command line arguments
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_dir = sys.argv[3]

    try:
        lat_lon_df = pd.read_csv(file1)
        speed_df = pd.read_csv(file2)
    except Exception as e:
        print(f"Error reading the files: {e}")
        sys.exit(1)

    print("lat_lon_df file:")    
    lat_lon_df['datetime_taken'] = pd.to_datetime(lat_lon_df['datetime_taken'], format='%Y:%m:%d %H:%M:%S').dt.floor('min')
    lat_lon_df.drop_duplicates(subset=['latitude','longitude'], keep='first', inplace = True)
    lat_lon_df = lat_lon_df.groupby('datetime_taken')['latitude','longitude'].mean().reset_index()
    print(lat_lon_df.head())
    print(lat_lon_df.dtypes)
    

    print("\nspeed_df file:")
    speed_df['End Time'] = pd.to_datetime(speed_df['End Time'], format='%d/%m/%Y %H:%M').dt.floor('min')
    speed_df = speed_df.groupby('End Time')['Download Speed (Mbit/s)'].mean().reset_index()
    print(speed_df.head())
    print(speed_df.dtypes)

    result = pd.merge(speed_df, lat_lon_df, how='left', left_on='End Time', right_on='datetime_taken')
    print(result)
    result = result.set_index('End Time')
    result['latitude'] = result['latitude'].interpolate(method='time')
    result['longitude'] = result['longitude'].interpolate(method='time')
    max_speed = max(result['Download Speed (Mbit/s)'])
    min_sped = min(result['Download Speed (Mbit/s)'])
    mean_lat = np.mean(result['latitude'])
    mean_lon = np.mean(result['longitude'])

    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=8)
    norm = matplotlib.colors.Normalize(vmin=min(result['Download Speed (Mbit/s)']), vmax=max(result['Download Speed (Mbit/s)']))
    colormap = matplotlib.cm.RdYlGn
    for lat, lon, size in zip(result['latitude'], result['longitude'], result['Download Speed (Mbit/s)']):
        # Create a color ranging from red to green based on size
        color = matplotlib.colors.rgb2hex(colormap(norm(size)))
        folium.CircleMarker(
            location=[lat, lon],
            radius=10, 
            color=color,
            fill=True,
            fill_opacity=1,
            fill_color=color
        ).add_to(m)

    m.save(f'{output_dir}/map.html') 

    print(result)
if __name__ == "__main__":
    main()

#python /Users/vitaly_lubimzev/Desktop/create_plot.py /Users/vitaly_lubimzev/Desktop/time_lat_lon.csv /Users/vitaly_lubimzev/Desktop/speed.csv /Users/vitaly_lubimzev/Desktop/