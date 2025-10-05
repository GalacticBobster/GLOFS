#Program to fetch CMAN data for a given year or date from the GL region
import os
import requests
from datetime import datetime, timedelta

'''
URL format =  https://www.ncei.noaa.gov/data/oceans/ndbc/co-ops/2025/01/NOS_1611400_202501_D1_v00.nc
'''

#Station ID around different lakes
NOS_id = ['9063020', '9063028', '9063038', '9063063', '9063079', '9063085', '9099004', '9099018', '9099044', '9099064', '9099090', '9075014', '9075065', '9075080', '9075099', '9087031', '9087088', '9087096', '9052000', '9052030', '9052058', '9052076']
year = '2022'
month = '12'

os.makedirs("../../CMAN", exist_ok=True)

for Nid in NOS_id:
    url = f"https://www.ncei.noaa.gov/data/oceans/ndbc/co-ops/{year}/{month}/NOS_{Nid}_{year}{month}_D1_v00.nc"
    fname = f"NOS_{Nid}_{year}{month}_D1_v00.nc"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../NOS/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Downloads Complete!")


