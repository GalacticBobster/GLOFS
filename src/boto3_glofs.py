import os
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime, timedelta

# Initialize S3 client for public access (no credentials)
s3 = boto3.client(
    "s3",
    config=Config(signature_version=UNSIGNED),
)

bucket = "noaa-nos-ofs-pds"

# Configuration
cycle_labels = ["t00z", "t06z", "t12z", "t18z"]
# Forecast steps or “nXXX” you want — here, e.g. 0 to 5 inclusive (i.e. n000 to n005)
forecast_steps = list(range(0, 6))

download_dir = "../downloads"
os.makedirs(download_dir, exist_ok=True)

def download_leofs_for_date(date: datetime):
    year = date.strftime("%Y")
    mon = date.strftime("%m")
    day = date.strftime("%d")
    ymd = date.strftime("%Y%m%d")

    lake = "leofs"
    prefix_dir = f"{lake}/netcdf/{year}/{mon}/{day}/"

    for cyc in cycle_labels:
        for step in forecast_steps:
            # format forecast-step with 3 digits, zero pad
            step_str = f"{step:03d}"
            fname = f"{lake}.{cyc}.{ymd}.fields.n{step_str}.nc"
            key = prefix_dir + fname
            local_path = os.path.join(download_dir, fname)

            print(f"Downloading s3://{bucket}/{key} → {local_path}")
            try:
                s3.download_file(bucket, key, local_path)
                print("  → Success")
            except Exception as e:
                print("  → Failed:", e)

def download_lsofs_for_date(date: datetime):
    # Similar logic for LSOFS, adjust naming if necessary
    year = date.strftime("%Y")
    mon = date.strftime("%m")
    day = date.strftime("%d")
    ymd = date.strftime("%Y%m%d")

    lake = "lsofs"
    prefix_dir = f"{lake}/netcdf/{year}/{mon}/{day}/"

    for cyc in cycle_labels:
        for step in forecast_steps:
            step_str = f"{step:03d}"
            fname = f"{lake}.{cyc}.{ymd}.fields.n{step_str}.nc"
            key = prefix_dir + fname
            local_path = os.path.join(download_dir, fname)

            print(f"Downloading s3://{bucket}/{key} → {local_path}")
            try:
                s3.download_file(bucket, key, local_path)
                print("  → Success")
            except Exception as e:
                print("  → Failed:", e)

def download_lmhofs_for_date(date: datetime):
    # Similar logic for LSOFS, adjust naming if necessary
    year = date.strftime("%Y")
    mon = date.strftime("%m")
    day = date.strftime("%d")
    ymd = date.strftime("%Y%m%d")

    lake = "lmhofs"
    prefix_dir = f"{lake}/netcdf/{year}/{mon}/{day}/"

    for cyc in cycle_labels:
        for step in forecast_steps:
            step_str = f"{step:03d}"
            fname = f"{lake}.{cyc}.{ymd}.fields.n{step_str}.nc"
            key = prefix_dir + fname
            local_path = os.path.join(download_dir, fname)

            print(f"Downloading s3://{bucket}/{key} → {local_path}")
            try:
                s3.download_file(bucket, key, local_path)
                print("  → Success")
            except Exception as e:
                print("  → Failed:", e)


def download_loofs_for_date(date: datetime):
    # Similar logic for LSOFS, adjust naming if necessary
    year = date.strftime("%Y")
    mon = date.strftime("%m")
    day = date.strftime("%d")
    ymd = date.strftime("%Y%m%d")

    lake = "loofs"
    prefix_dir = f"{lake}/netcdf/{year}/{mon}/{day}/"

    for cyc in cycle_labels:
        for step in forecast_steps:
            step_str = f"{step:03d}"
            fname = f"{lake}.{cyc}.{ymd}.fields.n{step_str}.nc"
            key = prefix_dir + fname
            local_path = os.path.join(download_dir, fname)

            print(f"Downloading s3://{bucket}/{key} → {local_path}")
            try:
                s3.download_file(bucket, key, local_path)
                print("  → Success")
            except Exception as e:
                print("  → Failed:", e)

if __name__ == "__main__":
    # Example: download for 2025-01-01
    dt = datetime(2025, 9, 5)
    download_leofs_for_date(dt)
    download_lsofs_for_date(dt)
    download_lmhofs_for_date(dt)
    download_loofs_for_date(dt)

