import os
import requests
from datetime import datetime, timedelta
import subprocess

base_date_str = "20221222"
base_date = datetime.strptime(base_date_str, "%Y%m%d")

end_date_str = "20221224"
end_date = datetime.strptime(end_date_str, "%Y%m%d")

year = base_date.strftime("%Y")
mon = base_date.strftime("%m")
day = base_date.strftime("%d")
date_tmp = base_date.strftime("%Y%j")


#RAP example: rap.t18z.wrfnatf00.grib2
#site example: https://noaa-rap-pds.s3.amazonaws.com/rap.20210314/rap.t00z.awp200f10.grib2
'''
The objective is to download data for each 00 cycle for all hours between start and stop time

'''

base_url = "https://noaa-rap-pds.s3.amazonaws.com"
cycles = range(0, 24)

output_dir = "../rap_downloads"
os.makedirs(output_dir, exist_ok=True)
cycl = "18"
fh = 0
while base_date <= end_date:
    ymd = base_date.strftime("%Y%m%d")
    yymmdd = base_date.strftime("%y%m%d")
    for cycle in cycles:
        cycle_str = f"{cycle:02d}"
        fh_str = "00"
        fh_corr = f"{fh:02d}"
        fh = fh + 1
# Build file name and S3 path
        filename = f"rap.t{cycle_str}z.wrfnatf{fh_str}.grib2"
        file_url = f"{base_url}/rap.{ymd}/{filename}"
        local_path = os.path.join(output_dir, filename)

#Change file name example: 22111612000000
        file_ch = f"{yymmdd}{cycl}000000"

            # Skip if file already exists
        if os.path.exists(local_path):
            print(f"Already downloaded: {filename}")
            continue
           # print(f"Downloading: {file_url}")
        else:
          print(f"Downloading: {file_url}")
          os.system(f"wget -q -O {local_path} {file_url}")
# Use AWS CLI to download the file
        #cmd = ["aws", "s3", "cp", "--no-sign-request", s3_path, "."]
        #print("Downloading:", s3_path)
        #subprocess.run(cmd)

    base_date += timedelta(days=1)
