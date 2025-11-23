"""
Fetch GLOFS (Great Lakes Operational Forecast System) data for multiple days.

This script extends the functionality of boto3_glofs.py to support fetching
data across multiple days for all Great Lakes.
"""

import os
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime, timedelta
from typing import List, Optional
import argparse


class GLOFSMultiDayFetcher:
    """Fetch GLOFS data for multiple days from AWS S3."""
    
    def __init__(self, download_dir: str = "../downloads"):
        """
        Initialize the fetcher.
        
        Args:
            download_dir: Directory to save downloaded files
        """
        self.s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        self.bucket = "noaa-nos-ofs-pds"
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Available lakes
        self.lakes = ["leofs", "lsofs", "lmhofs", "loofs"]
        self.cycle_labels = ["t00z", "t06z", "t12z", "t18z"]
        self.forecast_steps = list(range(0, 6))
    
    def generate_date_range(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        Generate a list of dates between start_date and end_date (inclusive).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of datetime objects
        """
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates
    
    def download_file(self, lake: str, date: datetime, cycle: str, step: int) -> str:
        """
        Download a single file from S3.
        
        Args:
            lake: Lake name (e.g., "leofs")
            date: Date to download
            cycle: Cycle label (e.g., "t00z")
            step: Forecast step (0-5)
            
        Returns:
            'success' if downloaded, 'exists' if already exists, 'failed' if failed
        """
        year = date.strftime("%Y")
        mon = date.strftime("%m")
        day = date.strftime("%d")
        ymd = date.strftime("%Y%m%d")
        
        step_str = f"{step:03d}"
        fname = f"{lake}.{cycle}.{ymd}.fields.n{step_str}.nc"
        prefix_dir = f"{lake}/netcdf/{year}/{mon}/{day}/"
        key = prefix_dir + fname
        local_path = os.path.join(self.download_dir, fname)
        
        # Skip if file already exists
        if os.path.exists(local_path):
            print(f"  → Already exists: {fname}")
            return "exists"
        
        print(f"Downloading s3://{self.bucket}/{key} → {local_path}")
        try:
            self.s3.download_file(self.bucket, key, local_path)
            print("  → Success")
            return "success"
        except Exception as e:
            print(f"  → Failed: {e}")
            return "failed"
    
    def fetch_lake_data(self, lake: str, start_date: datetime, end_date: datetime,
                       cycles: Optional[List[str]] = None,
                       forecast_steps: Optional[List[int]] = None) -> dict:
        """
        Fetch data for a specific lake across multiple days.
        
        Args:
            lake: Lake name (e.g., "leofs")
            start_date: Start date
            end_date: End date
            cycles: List of cycles to download (default: all)
            forecast_steps: List of forecast steps to download (default: 0-5)
            
        Returns:
            Dictionary with download statistics
        """
        if cycles is None:
            cycles = self.cycle_labels
        if forecast_steps is None:
            forecast_steps = self.forecast_steps
            
        dates = self.generate_date_range(start_date, end_date)
        
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        print(f"\n{'='*60}")
        print(f"Fetching {lake.upper()} data from {start_date.date()} to {end_date.date()}")
        print(f"{'='*60}")
        
        for date in dates:
            print(f"\nProcessing {lake} for {date.date()}")
            for cycle in cycles:
                for step in forecast_steps:
                    stats["total"] += 1
                    result = self.download_file(lake, date, cycle, step)
                    if result == "success":
                        stats["success"] += 1
                    elif result == "exists":
                        stats["skipped"] += 1
                    else:  # "failed"
                        stats["failed"] += 1
        
        return stats
    
    def fetch_all_lakes(self, start_date: datetime, end_date: datetime,
                       lakes: Optional[List[str]] = None,
                       cycles: Optional[List[str]] = None,
                       forecast_steps: Optional[List[int]] = None) -> dict:
        """
        Fetch data for all lakes across multiple days.
        
        Args:
            start_date: Start date
            end_date: End date
            lakes: List of lakes to download (default: all)
            cycles: List of cycles to download (default: all)
            forecast_steps: List of forecast steps to download (default: 0-5)
            
        Returns:
            Dictionary with download statistics for each lake
        """
        if lakes is None:
            lakes = self.lakes
            
        all_stats = {}
        
        for lake in lakes:
            stats = self.fetch_lake_data(lake, start_date, end_date, cycles, forecast_steps)
            all_stats[lake] = stats
            
        # Print summary
        print(f"\n{'='*60}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*60}")
        for lake, stats in all_stats.items():
            print(f"\n{lake.upper()}:")
            print(f"  Total files attempted: {stats['total']}")
            print(f"  Successfully downloaded: {stats['success']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Already existed: {stats['skipped']}")
            
        return all_stats


def main():
    """Main function to run the multi-day fetcher."""
    parser = argparse.ArgumentParser(
        description="Fetch GLOFS data for multiple days from AWS S3"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date in YYYYMMDD format (e.g., 20240101)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=True,
        help="End date in YYYYMMDD format (e.g., 20240107)"
    )
    parser.add_argument(
        "--lakes",
        type=str,
        nargs="+",
        default=None,
        choices=["leofs", "lsofs", "lmhofs", "loofs"],
        help="Lakes to download (default: all)"
    )
    parser.add_argument(
        "--cycles",
        type=str,
        nargs="+",
        default=None,
        choices=["t00z", "t06z", "t12z", "t18z"],
        help="Cycles to download (default: all)"
    )
    parser.add_argument(
        "--forecast-steps",
        type=int,
        nargs="+",
        default=None,
        help="Forecast steps to download (default: 0-5)"
    )
    parser.add_argument(
        "--download-dir",
        type=str,
        default="../downloads",
        help="Directory to save downloaded files (default: ../downloads)"
    )
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, "%Y%m%d")
        end_date = datetime.strptime(args.end_date, "%Y%m%d")
    except ValueError:
        print("Error: Dates must be in YYYYMMDD format")
        return
    
    if start_date > end_date:
        print("Error: Start date must be before or equal to end date")
        return
    
    # Initialize fetcher
    fetcher = GLOFSMultiDayFetcher(download_dir=args.download_dir)
    
    # Fetch data
    fetcher.fetch_all_lakes(
        start_date=start_date,
        end_date=end_date,
        lakes=args.lakes,
        cycles=args.cycles,
        forecast_steps=args.forecast_steps
    )


if __name__ == "__main__":
    main()
