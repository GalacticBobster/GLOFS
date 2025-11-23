#Program to fetch URMA data from AWS server


import os
from datetime import datetime, timedelta

# Define start 
start_date_str = "20250902"
start_hour = 18

end_date_str = "20250905"
end_hour = 18


start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")
base_url = "https://noaa-urma-pds.s3.amazonaws.com"
output_dir = "../../URMA"

'''
https://noaa-urma-pds.s3.amazonaws.com/urma2p5.20250215/urma2p5.t00z.2dvarges_ndfd.grb2_wexp
'''

os.makedirs(output_dir, exist_ok=True)

curr_dt = start_dt
while curr_dt <= end_dt:
    ymd = curr_dt.strftime("%Y%m%d")
    yymmdd = curr_dt.strftime("%y%m%d")
    hour = curr_dt.strftime("%H")
    day_url = f"urma2p5.{ymd}"
    filename = f"urma2p5.t{hour}z.2dvarges_ndfd.grb2_wexp"
    local_path = os.path.join(output_dir, filename)
    file_url = f"{base_url}/{day_url}/{filename}"
    new_filename = f"urma2p5.{yymmdd}.t{hour}z.2dvarges_ndfd.grb2_wexp"
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




