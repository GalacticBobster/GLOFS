import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os
from datetime import datetime, timedelta
import requests

# Create a client with unsigned config (no AWS credentials)
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
#s3 = boto3.client('s3', config=boto3.session.Config(signature_version='unsigned'))

start_date_str = "20230124"
start_hour = 0

end_date_str = "20230204"
end_hour = 0


start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")


'''
https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MergedReflectivityComposite_00.50/20201023/MRMS_MergedReflectivityComposite_00.50_20201023-000020.grib2.gz

https://noaa-mrms-pds.s3.amazonaws.com/
CONUS/
NLDN_CG_030min_AvgDensity_00.00/20201120/MRMS_NLDN_CG_030min_AvgDensity_00.00_20201120-000000.grib2.gz
'''


output_dir = "../../FLASH"
os.makedirs(output_dir, exist_ok=True)
base_url = 'https://noaa-mrms-pds.s3.amazonaws.com'
curr_dt = start_dt
cycl = 0
while curr_dt <= end_dt:
  ymd = curr_dt.strftime("%Y%m%d")
  hour = curr_dt.strftime("%H")
  response = s3.list_objects_v2(
    Bucket='noaa-mrms-pds',
    Prefix=f'CONUS/NLDN_CG_030min_AvgDensity_00.00/{ymd}/'
  )

  for obj in response.get('Contents', []):
    key = obj['Key']  # Full path to each file
    if f"MRMS_NLDN_CG_030min_AvgDensity_00.00_{ymd}-{hour}00" in key:
        print(key)
        file_url = f"{base_url}/{key}"
        local_file = os.path.join(output_dir, os.path.basename(key))
        print(f"Downloading {file_url}")
        try:
            with requests.get(file_url, stream=True) as r:
                 r.raise_for_status()
                 with open(local_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            print(f"Saved to {local_file}")
        except Exception as e:
            print(f"Failed to download {file_url}: {e}")
  curr_dt += timedelta(hours=1)

'''
output_dir = "../../MRMS"
os.makedirs(output_dir, exist_ok=True)

for key in file_keys:
    file_url = base_url + key
    local_filename = os.path.join(output_dir, os.path.basename(key))

    print(f"Downloading {file_url} ...")
    try:
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Saved to {local_filename}")
    except Exception as e:
        print(f"Failed to download {file_url}: {e}")
'''
