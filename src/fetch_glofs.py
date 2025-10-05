import os
import requests
from datetime import datetime, timedelta


base_date_str = "20240101"
base_date = datetime.strptime(base_date_str, "%Y%m%d")

year = base_date.strftime("%Y")
mon = base_date.strftime("%m")
day = base_date.strftime("%d")
date_tmp = base_date.strftime("%Y%j")

cycle_label = ["t00z","t06z","t12z","t18z"]

os.makedirs("../downloads", exist_ok=True)

#leofs
lakename = "model-leofs"
lake = "leofs"
#https://www.ncei.noaa.gov/thredds/fileServer/model-leofs/2022/12/nos.leofs.fields.n006.20221231.t18z.nc

for cycle in cycle_label:
  for i in range(0,6):
  #for i in range(0,1):
   fname = f"{lake}.{cycle}.{year}{mon}{day}.fields.n00{i}.nc"
   url = f"https://www.ncei.noaa.gov/thredds/fileServer/{lakename}/{year}/{mon}/{fname}"
   print(f"Downloading : {fname}")
   response = requests.get(url)
  
   if response.status_code == 200:
     with open(f"../downloads/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
   else:
     print(f"Failed to download {url} (status code {response.status_code})")

#lsofs
#https://www.ncei.noaa.gov/thredds/fileServer/model-lsofs-files/2025/06/lsofs.t18z.20250621.fields.n006.nc

lakename = "model-lsofs-files"
lake = "lsofs"

for cycle in cycle_label:
  for i in range(0,6):
  #for i in range(0,1):
   fname = f"{lake}.{cycle}.{year}{mon}{day}.fields.n00{i}.nc"
   url = f"https://www.ncei.noaa.gov/thredds/fileServer/{lakename}/{year}/{mon}/{fname}"
   print(f"Downloading : {fname}")
   response = requests.get(url)
  
   if response.status_code == 200:
     with open(f"../downloads/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
   else:
     print(f"Failed to download {url} (status code {response.status_code})")

#lhmofs
#https://www.ncei.noaa.gov/thredds/fileServer/model-lmhofs-files/2025/06/lmhofs.t18z.20250621.fields.n006.nc

lakename = "model-lmhofs-files"
lake = "lmhofs"

for cycle in cycle_label:
  for i in range(0,6):
  #for i in range(0,1):
   fname = f"{lake}.{cycle}.{year}{mon}{day}.fields.n00{i}.nc"
   url = f"https://www.ncei.noaa.gov/thredds/fileServer/{lakename}/{year}/{mon}/{fname}"
   print(f"Downloading : {fname}")
   response = requests.get(url)

   if response.status_code == 200:
     with open(f"../downloads/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
   else:
     print(f"Failed to download {url} (status code {response.status_code})")


#loofs
#https://www.ncei.noaa.gov/thredds/fileServer/model-loofs-files/2025/06/loofs.t18z.20250621.fields.n006.nc

lakename = "model-loofs-files"
lake = "loofs"

for cycle in cycle_label:
  for i in range(0,6):
  #for i in range(0,1):
   fname = f"{lake}.{cycle}.{year}{mon}{day}.fields.n00{i}.nc"
   url = f"https://www.ncei.noaa.gov/thredds/fileServer/{lakename}/{year}/{mon}/{fname}"
   print(f"Downloading : {fname}")
   response = requests.get(url)
  
   if response.status_code == 200:
     with open(f"../downloads/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
   else:
     print(f"Failed to download {url} (status code {response.status_code})")
