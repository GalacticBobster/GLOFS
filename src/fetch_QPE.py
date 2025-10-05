#Program to fetch URMA data from AWS server


import os
from datetime import datetime, timedelta

# Define start 
start_date_str = "20221222"
start_hour = 18

end_date_str = "20221225"
end_hour = 18


start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")
base_url = "https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MergedReflectivityQCComposite_00.50"
output_dir = "../../QPE"

'''
https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass1_00.00/20201015/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20201015-000000.grib2.gz
https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MergedReflectivityQCComposite_00.50/20201014/MRMS_MergedReflectivityQCComposite_00.50_20201014-211637.grib2.gz
'''

os.makedirs(output_dir, exist_ok=True)

curr_dt = start_dt
while curr_dt <= end_dt:
    ymd = curr_dt.strftime("%Y%m%d")
    yymmdd = curr_dt.strftime("%y%m%d")
    hour = curr_dt.strftime("%H")
    day_url = f"{ymd}"
    filename = f"MRMS_MergedReflectivityQCComposite_00.50_{ymd}-{hour}1637.grib2.gz"
    #filename = f"MRMS_MultiSensor_QPE_01H_Pass1_00.00_{ymd}-{hour}0000.grib2.gz"
    local_path = os.path.join(output_dir, filename)
    file_url = f"{base_url}/{day_url}/{filename}"
    new_filename = f"urma2p5.{yymmdd}.t{hour}z.2dvarges_ndfd.grb2_wexp"
    new_path = os.path.join(output_dir, filename)  
    # Download only if not already downloaded
    if os.path.exists(new_path):
        print(f"Already exists: {new_filename}")
    else:
        print(f"Downloading: {file_url}")
        os.system(f"wget -q -O {local_path} {file_url}")

    # Increment by 1 hour
    curr_dt += timedelta(hours=1)




