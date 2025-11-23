import os
from datetime import datetime, timedelta

# Define start and end
start_date_str = "20250902"
start_hour = 18

end_date_str = "20250905"
end_hour = 18

'''
https://noaa-hrrr-bdp-pds.s3.amazonaws.com/index.html#hrrr.20240106/conus/
# For the pressure level file (atmosphere)
hrrr.t{hour}z.wrfprsf00.grib2

# For the surface file
hrrr.t{hour}z.wrfsfcf00.grib2
'''
start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")

base_url = "https://noaa-hrrr-bdp-pds.s3.amazonaws.com"
output_dir = "../hrrr_downloads"
os.makedirs(output_dir, exist_ok=True)

curr_dt = start_dt
cycl = 0
while curr_dt <= end_dt:
    ymd = curr_dt.strftime("%Y%m%d")
    yymmdd = curr_dt.strftime("%y%m%d")
    hour = curr_dt.strftime("%H")
    filename = f"hrrr.t{hour}z.wrfprsf00.grib2"
    file_url = f"{base_url}/hrrr.{ymd}/conus/{filename}"
    local_path = os.path.join(output_dir, filename)

    # Rename format: yymmdd + hour + 000000
    new_filename = f"{yymmdd2}{start_hour:02d}{cycl:02d}0000"
    cycl = cycl + 1
    new_path = os.path.join(output_dir, new_filename)

    # Download only if not already downloaded
    if os.path.exists(new_path):
        print(f"Already exists: {new_filename}")
    else:
        print(f"Downloading: {file_url}")
        os.system(f"wget -q -O {local_path} {file_url}")

        # Rename if download succeeded
        if os.path.exists(local_path):
            os.rename(local_path, new_path)
            print(f"Renamed to: {new_filename}")
        else:
            print(f"Failed to download: {filename}")

    # Increment by 1 hour
    curr_dt += timedelta(hours=1)

