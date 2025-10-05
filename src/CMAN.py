#Program to fetch CMAN data for a given year or date from the GL region
import os
import requests
from datetime import datetime, timedelta

'''
URL format =  https://www.ndbc.noaa.gov/data/historical/stdmet/ygnn6h2024.txt.gz
https://www.ndbc.noaa.gov/data/stdmet/Feb/gtlm422025.txt.gz
'''

#Station ID around different lakes
#https://www.ndbc.noaa.gov/data/stdmet/Jan/twco112025.txt.gz
stations = ['APNM4', 'BUFN6', 'CNDO1', 'DBLN6', 'DULM5', 'GRMM4', 'GTLM4', 'GTRM4', 'MCYI3', 'MEEM4', 'MNMM4', 'PWAW3', 'SBLM4', 'TBIM4', 'THLO1']

year = '2025'
month = '1'
month_name = 'Jan'
os.makedirs("../../CMAN", exist_ok=True)

for station in stations:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/stdmet/{month_name}/{station_lower}{month}{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")


