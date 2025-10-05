import boto3
from botocore import UNSIGNED
from botocore.config import Config
import os
from datetime import datetime, timedelta
import requests

# Create a client with unsigned config (no AWS credentials)
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
#s3 = boto3.client('s3', config=boto3.session.Config(signature_version='unsigned'))

start_date_str = "20220101"
start_hour = 0

end_date_str = "20220105"
end_hour = 0


start_dt = datetime.strptime(start_date_str + f"{start_hour:02d}", "%Y%m%d%H")
end_dt = datetime.strptime(end_date_str + f"{end_hour:02d}", "%Y%m%d%H")

yymmdd2 = start_dt.strftime("%y%m%d")


'''
https://noaa-goes18.s3.amazonaws.com/GLM-L2-LCFA/2022/288/23/OR_GLM-L2-LCFA_G18_s20222882300000_e20222882300200_c20222882300216.nc
https://noaa-goes16.s3.amazonaws.com/GLM-L2-LCFA/2022/005/04/OR_GLM-L2-LCFA_G16_s20220050400400_e20220050401000_c20220050401027.nc
'''


output_dir = "../../FLASH"
os.makedirs(output_dir, exist_ok=True)
base_url = 'https://noaa-goes16.s3.amazonaws.com'
curr_dt = start_dt
cycl = 0
while curr_dt <= end_dt:
  ymd = curr_dt.strftime("%Y%m%d")
  hour = curr_dt.strftime("%H")
  doy = curr_dt.strftime("%j")
  response = s3.list_objects_v2(
    Bucket='noaa-goes16',
    Prefix=f'GLM-L2-LCFA/{curr_dt.year}/{doy}/{hour}/'
  )
  for obj in response.get('Contents', []):
    key = obj['Key']  # Full path to each file
    if f"OR_GLM-L2-LCFA_G18_s" in key:
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
