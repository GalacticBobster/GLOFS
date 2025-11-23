#!/usr/bin/env python3
"""
Quick start example for GLOFS Lake Data Fetcher and LSTM Model.

This script demonstrates basic usage with minimal setup.
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
from fetch_lake_data_multiday import GLOFSMultiDayFetcher
from lake_data_preprocessor import GLOFSDataPreprocessor


def example_1_fetch_data():
    """Example 1: Fetch lake data for a few days."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Fetch Lake Data")
    print("="*60)
    
    # Initialize fetcher
    fetcher = GLOFSMultiDayFetcher(download_dir="./downloads")
    
    # Fetch data for Lake Erie for 3 days
    start_date = datetime.now() - timedelta(days=10)  # 10 days ago
    end_date = start_date + timedelta(days=2)  # 3 days total
    
    print(f"\nFetching Lake Erie (LEOFS) data...")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Fetch only a couple of files for demonstration
    stats = fetcher.fetch_lake_data(
        lake="leofs",
        start_date=start_date,
        end_date=end_date,
        cycles=["t00z"],  # Only one cycle per day
        forecast_steps=[0, 1]  # Only first two forecast steps
    )
    
    print(f"\nResults:")
    print(f"  Downloaded: {stats['success']}")
    print(f"  Already existed: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")


def example_2_inspect_data():
    """Example 2: Inspect downloaded NetCDF files."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Inspect NetCDF Data")
    print("="*60)
    
    preprocessor = GLOFSDataPreprocessor(data_dir="./downloads")
    
    # List available files
    files = preprocessor.list_files(lake="leofs")
    
    if not files:
        print("\nNo files found. Run Example 1 first to download data.")
        return
    
    print(f"\nFound {len(files)} files")
    print(f"First file: {os.path.basename(files[0])}")
    
    # Inspect variables in first file
    print("\nInspecting variables in first file...")
    var_info = preprocessor.inspect_variables(files[0])
    
    print(f"\nAvailable variables ({len(var_info)} total):")
    for var_name, info in list(var_info.items())[:5]:  # Show first 5
        print(f"  {var_name}:")
        print(f"    - Shape: {info['shape']}")
        print(f"    - Dtype: {info['dtype']}")
        if 'long_name' in info['attrs']:
            print(f"    - Description: {info['attrs']['long_name']}")


def example_3_extract_timeseries():
    """Example 3: Extract time series data."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extract Time Series")
    print("="*60)
    
    preprocessor = GLOFSDataPreprocessor(data_dir="./downloads")
    
    files = preprocessor.list_files(lake="leofs")
    
    if not files:
        print("\nNo files found. Run Example 1 first to download data.")
        return
    
    # Get list of variables from first file
    var_info = preprocessor.inspect_variables(files[0])
    
    if not var_info:
        print("\nNo variables found in files.")
        return
    
    # Try to extract temperature or use first available variable
    if 'temp' in var_info:
        variable = 'temp'
    elif 'zeta' in var_info:
        variable = 'zeta'
    else:
        variable = list(var_info.keys())[0]
    
    print(f"\nExtracting time series for variable: {variable}")
    
    df = preprocessor.extract_variable_timeseries(
        lake="leofs",
        variable=variable,
        aggregation="mean"
    )
    
    if df.empty:
        print("No data extracted.")
        return
    
    print(f"\nExtracted {len(df)} time steps")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nStatistics:")
    print(df[variable].describe())
    
    # Save to CSV
    output_file = f"./leofs_{variable}_timeseries.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to: {output_file}")


def example_4_prepare_for_lstm():
    """Example 4: Prepare data for LSTM training."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Prepare Data for LSTM")
    print("="*60)
    
    preprocessor = GLOFSDataPreprocessor(data_dir="./downloads")
    
    files = preprocessor.list_files(lake="leofs")
    
    if not files:
        print("\nNo files found. Run Example 1 first to download data.")
        return
    
    # Get a variable to work with
    var_info = preprocessor.inspect_variables(files[0])
    if 'temp' in var_info:
        variable = 'temp'
    elif 'zeta' in var_info:
        variable = 'zeta'
    else:
        variable = list(var_info.keys())[0]
    
    # Extract time series
    df = preprocessor.extract_variable_timeseries(
        lake="leofs",
        variable=variable,
        aggregation="mean"
    )
    
    if df.empty or len(df) < 50:
        print(f"\nNot enough data (need at least 50 samples, got {len(df)}).")
        print("Fetch more data with Example 1 first.")
        return
    
    print(f"\nPreparing data for LSTM training...")
    print(f"Variable: {variable}")
    print(f"Total samples: {len(df)}")
    
    # Prepare for LSTM
    data_dict = preprocessor.prepare_lstm_data(
        df=df,
        target_variable=variable,
        sequence_length=10,  # Shorter sequence for demo
        train_split=0.8
    )
    
    print(f"\nData prepared:")
    print(f"  X_train shape: {data_dict['X_train'].shape}")
    print(f"  y_train shape: {data_dict['y_train'].shape}")
    print(f"  X_test shape: {data_dict['X_test'].shape}")
    print(f"  y_test shape: {data_dict['y_test'].shape}")
    print(f"  Features: {data_dict['feature_names']}")
    print(f"  Target: {data_dict['target_variable']}")
    
    print("\nData is ready for LSTM training!")
    print("To train a model, install TensorFlow: pip install tensorflow")
    print("Then use the train_lstm_model function from lake_lstm_model.py")


def example_5_inspect_node_coordinates():
    """Example 5: Inspect node coordinates for mapping."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Inspect Node Coordinates")
    print("="*60)
    
    preprocessor = GLOFSDataPreprocessor(data_dir="./downloads")
    
    files = preprocessor.list_files(lake="leofs")
    
    if not files:
        print("\nNo files found. Run Example 1 first to download data.")
        return
    
    print("\nInspecting node coordinates for Lake Erie (LEOFS)...")
    
    # Get node summary
    node_summary = preprocessor.inspect_nodes(lake="leofs", output_format="summary")
    
    if not node_summary:
        print("Could not load node coordinates.")
        return
    
    print(f"\nNode coordinate summary:")
    print(f"  Total nodes: {node_summary['num_nodes']:,}")
    print(f"  Latitude range: {node_summary['latitude_range'][0]:.4f}°N to {node_summary['latitude_range'][1]:.4f}°N")
    print(f"  Longitude range: {node_summary['longitude_range'][0]:.4f}°E to {node_summary['longitude_range'][1]:.4f}°E")
    
    # Inspect a specific node
    print("\nInspecting node #100:")
    node_info = preprocessor.get_node_info(lake="leofs", node_index=100, include_sample_data=True)
    
    if node_info:
        print(f"  Latitude: {node_info['latitude']:.6f}°N")
        print(f"  Longitude: {node_info['longitude']:.6f}°E")
        if 'sample_data' in node_info and node_info['sample_data']:
            print(f"  Sample data:")
            for var, val in list(node_info['sample_data'].items())[:3]:
                print(f"    {var}: {val:.4f}")
    
    # Find nodes in a region
    print("\nFinding nodes in central Lake Erie (41.5°N-42.5°N, -81.5°W to -80.5°W):")
    region_result = preprocessor.find_nodes_in_region(
        lake="leofs",
        lat_min=41.5, lat_max=42.5,
        lon_min=-81.5, lon_max=-80.5
    )
    
    if region_result:
        print(f"  Found {region_result['num_nodes_in_region']} nodes in this region")
        if region_result['num_nodes_in_region'] > 0:
            print(f"  First 3 nodes:")
            for node in region_result['node_coordinates'][:3]:
                print(f"    Node {node['node_index']}: ({node['lat']:.4f}°N, {node['lon']:.4f}°E)")
    
    print("\nFor more detailed node inspection, use: python inspect_node_coordinates.py --help")


def main():
    """Run all examples."""
    print("\n" + "#"*60)
    print("# GLOFS Lake Data Fetcher - Quick Start Examples")
    print("#"*60)
    
    import argparse
    parser = argparse.ArgumentParser(description="Quick start examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific example (1-5). If not specified, runs all."
    )
    args = parser.parse_args()
    
    try:
        if args.example == 1 or args.example is None:
            example_1_fetch_data()
        
        if args.example == 2 or args.example is None:
            example_2_inspect_data()
        
        if args.example == 3 or args.example is None:
            example_3_extract_timeseries()
        
        if args.example == 4 or args.example is None:
            example_4_prepare_for_lstm()
        
        if args.example == 5 or args.example is None:
            example_5_inspect_node_coordinates()
        
        print("\n" + "#"*60)
        print("# Examples completed!")
        print("#"*60)
        print("\nNext steps:")
        print("  1. Explore the downloaded data in ./downloads/")
        print("  2. Check the CSV output files")
        print("  3. Install TensorFlow for LSTM training: pip install tensorflow")
        print("  4. Run the full workflow: python src/example_lstm_workflow.py --help")
        print("  5. Inspect node coordinates: python inspect_node_coordinates.py --help")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
