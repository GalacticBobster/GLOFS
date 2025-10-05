#Program to fetch CMAN data for a given year or date from the GL region
import os
import requests
from datetime import datetime, timedelta

'''
URL format =  https://www.ndbc.noaa.gov/data/historical/stdmet/ygnn6h2024.txt.gz

'''

#Station ID around different lakes

Ontario = ['YGNN6', 'OLCN6', 'RPRN6', 'OSGN6', 'CAVN6']
Erie = ['BUFN6', 'PSTN6', 'DBLN6', 'BARN6', 'CBLO1', 'ASBO1', 'GELO1', 'FAIO1', 'CNDO1', 'LORO1', 'VRMO1', 'HHLO1', 'MRHO1', 'SBIO1', 'CMPO1', 'TWCO1']
Superior = ['PTIM4', 'WFPM4', 'GRMM4', 'KP53', 'MCGM4', 'BIGM4', 'KP59', 'PCLM4', 'OTNM4', 'DISW3', 'PNGW3', 'BILW3', 'DULM5']
Michigan = ['CMTI2', 'BHRI3', 'SVNM4', 'HLNM4', 'MKGM4', 'LDTM4', 'BSBM4', 'MEEM4', 'GTLM4']
Huron = ['MACM4', 'CYGM4']

year = '2022'

os.makedirs("../../CMAN", exist_ok=True)

for station in Huron:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_lower}h{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to downloads/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Lake Huron done!")

for station in Michigan:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_lower}h{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to ../../CMAN/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Lake Michigan done!")

for station in Superior:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_lower}h{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to ../../CMAN/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Lake Superior done!")

for station in Erie:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_lower}h{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to ../../CMAN/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Lake Erie done!")


for station in Ontario:
    station_lower = station.lower()
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_lower}h{year}.txt.gz"
    fname = f"{station_lower}h{year}.txt.gz"
    print(f"Downloading : {fname}")
    response = requests.get(url)

    if response.status_code == 200:
     with open(f"../../CMAN/{fname}", "wb") as f:
        f.write(response.content)
     print(f"Saved to ../../CMAN/{fname}")
    else:
     print(f"Failed to download {url} (status code {response.status_code})")

print("Lake Ontario done!")

