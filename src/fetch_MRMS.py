import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


# Define start and end
start_date_str = "20221117"
start_hour = 18

end_date_str = "20221120"
end_hour = 18


start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")


'''
https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MergedReflectivityComposite_00.50/20201023/MRMS_MergedReflectivityComposite_00.50_20201023-000020.grib2.gz

NLDN_CG_030min_AvgDensity_00.00/
https://noaa-mrms-pds.s3.amazonaws.com/CONUS/NLDN_CG_030min_AvgDensity_00.00/20201120/MRMS_NLDN_CG_030min_AvgDensity_00.00_20201120-232413.grib2.gz

'''


output_dir = "../../FLASH"
os.makedirs(output_dir, exist_ok=True)

curr_dt = start_dt
cycl = 0
while curr_dt <= end_dt:
    ymd = curr_dt.strftime("%Y%m%d")
    yymmdd = curr_dt.strftime("%y%m%d")
    hour = curr_dt.strftime("%H")
    base_url = f"https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MergedReflectivityComposite_00.50/{ymd}/"
    prefix = f"MRMS_MergedReflectivityComposite_00.50_{yymmdd2}-{hour}00"
    # Step 1: Get HTML page
    response = requests.get(base_url)
    # Step 2: Search for matching file
    soup = BeautifulSoup(response.text, features='xml')
    file_url = None

    for key_tag in soup.find_all('Key'):
        key = key_tag.text
        print(key)
        if key.startswith(f"CONUS/MergedReflectivityComposite_00.50/{ymd}/{prefix}"):
            file_url = f"https://noaa-mrms-pds.s3.amazonaws.com/{key}"
            break

    # Step 3: Download file if found
    if file_url:
        print(f"Found file: {file_url}")
        out_dir = '../../MRMS'
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, os.path.basename(file_url))

        try:
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()
                with open(out_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Downloaded to {out_file}")
        except requests.RequestException as e:
            print(f"Download failed: {e}")
    else:
        print(f"No matching file found for {curr_dt.strftime('%Y-%m-%d %H:%M')}")





    # Increment by 1 hour
    curr_dt += timedelta(hours=1)

