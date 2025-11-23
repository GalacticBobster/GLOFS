"""
Complete example script for fetching lake data and training LSTM models.

This script demonstrates the full workflow:
1. Fetch lake data for multiple days
2. Extract and preprocess variables
3. Train LSTM model for prediction
"""

import os
import sys
from datetime import datetime, timedelta
import argparse
import pandas as pd
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_lake_data_multiday import GLOFSMultiDayFetcher
from lake_data_preprocessor import GLOFSDataPreprocessor
from lake_lstm_model import train_lstm_model


def run_complete_workflow(
    start_date: str,
    end_date: str,
    lake: str = "leofs",
    variable: str = "temp",
    download_dir: str = "../downloads",
    output_dir: str = "../output",
    sequence_length: int = 24,
    lstm_units: list = None,
    epochs: int = 100,
    batch_size: int = 32
):
    """
    Run the complete workflow from data fetching to model training.
    
    Args:
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format
        lake: Lake name (leofs, lsofs, lmhofs, loofs)
        variable: Variable to predict (e.g., temp, zeta, u, v)
        download_dir: Directory for downloaded files
        output_dir: Directory for output files
        sequence_length: Length of input sequences
        lstm_units: List of LSTM units per layer
        epochs: Number of training epochs
        batch_size: Batch size for training
    """
    if lstm_units is None:
        lstm_units = [50, 50]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("GLOFS LSTM MODEL TRAINING WORKFLOW")
    print("="*80)
    print(f"Lake: {lake}")
    print(f"Variable: {variable}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Sequence length: {sequence_length}")
    print(f"LSTM units: {lstm_units}")
    print("="*80)
    
    # Step 1: Fetch data
    print("\nSTEP 1: Fetching data...")
    print("-"*80)
    
    fetcher = GLOFSMultiDayFetcher(download_dir=download_dir)
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    
    stats = fetcher.fetch_lake_data(lake, start_dt, end_dt)
    
    print(f"\nDownload complete:")
    print(f"  Total files attempted: {stats['total']}")
    print(f"  Successfully downloaded: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    
    # Step 2: Preprocess data
    print("\nSTEP 2: Preprocessing data...")
    print("-"*80)
    
    preprocessor = GLOFSDataPreprocessor(data_dir=download_dir)
    
    # List available files
    files = preprocessor.list_files(lake=lake)
    print(f"Found {len(files)} NetCDF files for {lake}")
    
    if not files:
        print("ERROR: No files found. Cannot proceed.")
        return
    
    # Inspect first file to see available variables
    print("\nInspecting available variables in first file...")
    var_info = preprocessor.inspect_variables(files[0])
    print("\nAvailable variables:")
    for var_name, info in var_info.items():
        print(f"  {var_name}: shape={info['shape']}, dtype={info['dtype']}")
    
    # Check if target variable exists
    if variable not in var_info:
        print(f"\nWARNING: Variable '{variable}' not found in files.")
        print(f"Available variables: {list(var_info.keys())}")
        print("Using first available variable instead...")
        if var_info:
            variable = list(var_info.keys())[0]
            print(f"Selected variable: {variable}")
        else:
            print("ERROR: No variables available.")
            return
    
    # Extract time series
    print(f"\nExtracting time series for variable: {variable}")
    df = preprocessor.extract_variable_timeseries(
        lake=lake,
        variable=variable,
        aggregation="mean"
    )
    
    if df.empty:
        print("ERROR: No data extracted. Cannot proceed.")
        return
    
    print(f"Extracted {len(df)} time steps")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"\nData summary:")
    print(df.describe())
    
    # Save raw time series
    csv_path = os.path.join(output_dir, f"{lake}_{variable}_timeseries.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nRaw time series saved to: {csv_path}")
    
    # Step 3: Prepare LSTM data
    print("\nSTEP 3: Preparing data for LSTM...")
    print("-"*80)
    
    # Check if we have enough data
    min_samples = sequence_length + 100  # Need at least sequence_length + some test data
    if len(df) < min_samples:
        print(f"ERROR: Not enough data. Need at least {min_samples} samples, got {len(df)}")
        return
    
    data_dict = preprocessor.prepare_lstm_data(
        df=df,
        target_variable=variable,
        feature_variables=[variable],  # Using only the target variable as feature
        sequence_length=sequence_length,
        train_split=0.8
    )
    
    print(f"Training samples: {len(data_dict['X_train'])}")
    print(f"Test samples: {len(data_dict['X_test'])}")
    print(f"Features: {data_dict['feature_names']}")
    print(f"Input shape: {data_dict['X_train'].shape}")
    
    # Step 4: Train LSTM model
    print("\nSTEP 4: Training LSTM model...")
    print("-"*80)
    
    model_path = os.path.join(output_dir, f"{lake}_{variable}_lstm_model.h5")
    plot_dir = os.path.join(output_dir, "plots")
    
    try:
        model, metrics = train_lstm_model(
            data_dict=data_dict,
            lstm_units=lstm_units,
            dropout=0.2,
            learning_rate=0.001,
            epochs=epochs,
            batch_size=batch_size,
            early_stopping_patience=10,
            model_save_path=model_path,
            plot_save_dir=plot_dir
        )
        
        print("\nTraining complete!")
        print(f"Model saved to: {model_path}")
        print(f"Plots saved to: {plot_dir}")
        
        # Save metrics
        metrics_path = os.path.join(output_dir, f"{lake}_{variable}_metrics.txt")
        with open(metrics_path, 'w') as f:
            f.write(f"LSTM Model Metrics for {lake} - {variable}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Sequence Length: {sequence_length}\n")
            f.write(f"LSTM Units: {lstm_units}\n")
            f.write(f"Training Samples: {len(data_dict['X_train'])}\n")
            f.write(f"Test Samples: {len(data_dict['X_test'])}\n\n")
            f.write("Test Metrics:\n")
            for key, value in metrics.items():
                f.write(f"  {key}: {value:.6f}\n")
        
        print(f"Metrics saved to: {metrics_path}")
        
    except ImportError as e:
        print(f"\nERROR: {e}")
        print("Install TensorFlow with: pip install tensorflow")
        return
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE!")
    print("="*80)


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Fetch lake data and train LSTM model for prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch data and train model for Lake Erie (leofs) temperature
  python example_lstm_workflow.py --start-date 20240101 --end-date 20240107 --lake leofs --variable temp
  
  # Train with custom LSTM architecture
  python example_lstm_workflow.py --start-date 20240101 --end-date 20240107 --lake lsofs --lstm-units 64 64 32
  
  # Quick test with fewer epochs
  python example_lstm_workflow.py --start-date 20240101 --end-date 20240103 --lake leofs --epochs 10
        """
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
        "--lake",
        type=str,
        default="leofs",
        choices=["leofs", "lsofs", "lmhofs", "loofs"],
        help="Lake to analyze (default: leofs)"
    )
    parser.add_argument(
        "--variable",
        type=str,
        default="temp",
        help="Variable to predict (default: temp). Common variables: temp, zeta, u, v"
    )
    parser.add_argument(
        "--download-dir",
        type=str,
        default="../downloads",
        help="Directory for downloaded files (default: ../downloads)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="../output",
        help="Directory for output files (default: ../output)"
    )
    parser.add_argument(
        "--sequence-length",
        type=int,
        default=24,
        help="Length of input sequences (default: 24)"
    )
    parser.add_argument(
        "--lstm-units",
        type=int,
        nargs="+",
        default=[50, 50],
        help="LSTM units per layer (default: 50 50)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for training (default: 32)"
    )
    
    args = parser.parse_args()
    
    # Run workflow
    run_complete_workflow(
        start_date=args.start_date,
        end_date=args.end_date,
        lake=args.lake,
        variable=args.variable,
        download_dir=args.download_dir,
        output_dir=args.output_dir,
        sequence_length=args.sequence_length,
        lstm_units=args.lstm_units,
        epochs=args.epochs,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
