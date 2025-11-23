#!/usr/bin/env python3
"""
Node Coordinate Inspector for GLOFS Data

This script demonstrates how to inspect node coordinates (latitude/longitude)
from GLOFS NetCDF files for mapping purposes.

Usage:
    python inspect_node_coordinates.py --lake leofs
    python inspect_node_coordinates.py --lake leofs --node 100
    python inspect_node_coordinates.py --lake leofs --region 41.5 42.5 -81.5 -80.5
    python inspect_node_coordinates.py --lake leofs --export-coords nodes.csv
"""

import os
import sys
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lake_data_preprocessor import GLOFSDataPreprocessor
import pandas as pd


def format_lon(lon: float) -> str:
    """Format longitude for Western Hemisphere (Great Lakes use negative values = West)."""
    return f"{abs(lon):.4f}°W" if lon < 0 else f"{lon:.4f}°E"


def format_lon_precise(lon: float) -> str:
    """Format longitude with more precision."""
    return f"{abs(lon):.6f}°W" if lon < 0 else f"{lon:.6f}°E"


def inspect_lake_nodes(lake: str, data_dir: str = "./downloads"):
    """
    Display summary of node coordinates for a lake.
    
    Args:
        lake: Lake name (e.g., "leofs")
        data_dir: Directory containing NetCDF files
    """
    preprocessor = GLOFSDataPreprocessor(data_dir=data_dir)
    
    print("="*70)
    print(f"NODE COORDINATE INSPECTION: {lake.upper()}")
    print("="*70)
    
    # Get node coordinate summary
    node_summary = preprocessor.inspect_nodes(lake=lake, output_format="summary")
    
    if not node_summary:
        print(f"\nError: Could not load coordinate data for {lake}")
        print(f"Make sure NetCDF files exist in {data_dir}")
        return None
    
    print(f"\nLake: {node_summary['lake'].upper()}")
    print(f"Total nodes: {node_summary['num_nodes']:,}")
    print(f"\nGeographic extent:")
    print(f"  Latitude:  {node_summary['latitude_range'][0]:.4f}°N to {node_summary['latitude_range'][1]:.4f}°N")
    print(f"  Longitude: {format_lon(node_summary['longitude_range'][0])} to {format_lon(node_summary['longitude_range'][1])}")
    print(f"\nSource file: {os.path.basename(node_summary['source_file'])}")
    
    return node_summary


def inspect_specific_node(lake: str, node_index: int, 
                         data_dir: str = "./downloads",
                         include_data: bool = True):
    """
    Display detailed information about a specific node.
    
    Args:
        lake: Lake name
        node_index: Node index to inspect
        data_dir: Directory containing NetCDF files
        include_data: Whether to include sample data values
    """
    preprocessor = GLOFSDataPreprocessor(data_dir=data_dir)
    
    print("\n" + "="*70)
    print(f"NODE DETAILS: {lake.upper()} - Node #{node_index}")
    print("="*70)
    
    node_info = preprocessor.get_node_info(
        lake=lake, 
        node_index=node_index,
        include_sample_data=include_data
    )
    
    if not node_info:
        return
    
    print(f"\nNode index: {node_info['node_index']}")
    print(f"Latitude:   {node_info['latitude']:.6f}°N")
    print(f"Longitude:  {format_lon_precise(node_info['longitude'])}")
    
    if include_data and 'sample_data' in node_info:
        print(f"\nSample data from first available file:")
        if node_info['sample_data']:
            for var_name, value in sorted(node_info['sample_data'].items()):
                print(f"  {var_name:20s}: {value:12.4f}")
        else:
            print("  (No sample data available)")
        print(f"\nData source: {os.path.basename(node_info['sample_data_source'])}")


def find_nodes_in_region(lake: str, lat_min: float, lat_max: float,
                        lon_min: float, lon_max: float,
                        data_dir: str = "./downloads",
                        max_display: int = 10):
    """
    Find and display nodes in a geographic region.
    
    Args:
        lake: Lake name
        lat_min, lat_max: Latitude bounds
        lon_min, lon_max: Longitude bounds
        data_dir: Directory containing NetCDF files
        max_display: Maximum number of nodes to display
    """
    preprocessor = GLOFSDataPreprocessor(data_dir=data_dir)
    
    print("\n" + "="*70)
    print(f"NODES IN REGION: {lake.upper()}")
    print("="*70)
    
    result = preprocessor.find_nodes_in_region(
        lake=lake,
        lat_min=lat_min, lat_max=lat_max,
        lon_min=lon_min, lon_max=lon_max
    )
    
    if not result:
        return None
    
    print(f"\nRegion bounds:")
    print(f"  Latitude:  {lat_min:.4f}°N to {lat_max:.4f}°N")
    print(f"  Longitude: {format_lon(lon_min)} to {format_lon(lon_max)}")
    print(f"\nNodes found: {result['num_nodes_in_region']:,}")
    
    if result['num_nodes_in_region'] > 0:
        display_count = min(max_display, result['num_nodes_in_region'])
        print(f"\nFirst {display_count} nodes:")
        print(f"{'Index':>8s}  {'Latitude':>10s}  {'Longitude':>12s}")
        print("-" * 36)
        for node in result['node_coordinates'][:display_count]:
            print(f"{node['node_index']:8d}  {node['lat']:10.4f}  {format_lon(node['lon']):>12s}")
        
        if result['num_nodes_in_region'] > max_display:
            print(f"... and {result['num_nodes_in_region'] - max_display} more nodes")
    
    return result


def export_all_coordinates(lake: str, output_file: str, 
                          data_dir: str = "./downloads"):
    """
    Export all node coordinates to a CSV file.
    
    Args:
        lake: Lake name
        output_file: Path to output CSV file
        data_dir: Directory containing NetCDF files
    """
    preprocessor = GLOFSDataPreprocessor(data_dir=data_dir)
    
    print("\n" + "="*70)
    print(f"EXPORTING COORDINATES: {lake.upper()}")
    print("="*70)
    
    # Get full coordinate data
    node_data = preprocessor.inspect_nodes(lake=lake, output_format="full")
    
    if not node_data or 'lat' not in node_data:
        print(f"\nError: Could not load coordinate data for {lake}")
        return
    
    # Create DataFrame
    df = pd.DataFrame({
        'node_index': range(len(node_data['lat'])),
        'latitude': node_data['lat'],
        'longitude': node_data['lon']
    })
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"\nExported {len(df):,} node coordinates to: {output_file}")
    print(f"\nFirst few rows:")
    print(df.head(10).to_string(index=False))


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Inspect node coordinates from GLOFS NetCDF files for mapping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Display summary of all nodes for Lake Erie
  python inspect_node_coordinates.py --lake leofs
  
  # Inspect a specific node
  python inspect_node_coordinates.py --lake leofs --node 100
  
  # Find nodes in a geographic region (lat_min lat_max lon_min lon_max)
  python inspect_node_coordinates.py --lake leofs --region 41.5 42.5 -81.5 -80.5
  
  # Export all coordinates to CSV
  python inspect_node_coordinates.py --lake leofs --export-coords leofs_nodes.csv
  
  # Combine options
  python inspect_node_coordinates.py --lake lsofs --node 50 --export-coords lsofs_coords.csv

Lake abbreviations:
  leofs  = Lake Erie
  lsofs  = Lake Superior
  lmhofs = Lake Michigan-Huron
  loofs  = Lake Ontario
        """
    )
    
    parser.add_argument(
        "--lake",
        type=str,
        required=True,
        choices=["leofs", "lsofs", "lmhofs", "loofs"],
        help="Lake to inspect"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./downloads",
        help="Directory containing NetCDF files (default: ./downloads)"
    )
    parser.add_argument(
        "--node",
        type=int,
        help="Specific node index to inspect in detail"
    )
    parser.add_argument(
        "--region",
        type=float,
        nargs=4,
        metavar=("LAT_MIN", "LAT_MAX", "LON_MIN", "LON_MAX"),
        help="Find nodes in region: lat_min lat_max lon_min lon_max"
    )
    parser.add_argument(
        "--export-coords",
        type=str,
        metavar="OUTPUT_FILE",
        help="Export all node coordinates to CSV file"
    )
    parser.add_argument(
        "--max-display",
        type=int,
        default=10,
        help="Maximum nodes to display when searching region (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Always show lake summary first
    inspect_lake_nodes(lake=args.lake, data_dir=args.data_dir)
    
    # Inspect specific node if requested
    if args.node is not None:
        inspect_specific_node(
            lake=args.lake,
            node_index=args.node,
            data_dir=args.data_dir,
            include_data=True
        )
    
    # Find nodes in region if requested
    if args.region:
        lat_min, lat_max, lon_min, lon_max = args.region
        find_nodes_in_region(
            lake=args.lake,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            data_dir=args.data_dir,
            max_display=args.max_display
        )
    
    # Export coordinates if requested
    if args.export_coords:
        export_all_coordinates(
            lake=args.lake,
            output_file=args.export_coords,
            data_dir=args.data_dir
        )
    
    print("\n" + "="*70)
    print("INSPECTION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
