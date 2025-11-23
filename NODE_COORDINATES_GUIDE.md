# Node Coordinate Inspection for GLOFS Data

This document explains how to inspect node coordinates (latitude/longitude) from GLOFS NetCDF files for mapping and geographic analysis.

## Overview

GLOFS (Great Lakes Operational Forecast System) data uses an unstructured FVCOM (Finite Volume Community Ocean Model) mesh. Each node in the mesh represents a geographic location with associated latitude and longitude coordinates. This functionality allows you to:

- View the geographic extent of a lake's mesh
- Inspect coordinates for specific nodes
- Find nodes within a geographic region
- Export all coordinates for mapping/visualization

## Quick Start

### 1. Download Some Data First

```bash
# Fetch some GLOFS data
python quick_start_examples.py --example 1
```

### 2. Inspect Node Coordinates

```bash
# View summary for Lake Erie
python inspect_node_coordinates.py --lake leofs

# Inspect a specific node
python inspect_node_coordinates.py --lake leofs --node 100

# Find nodes in a region (lat_min lat_max lon_min lon_max)
python inspect_node_coordinates.py --lake leofs --region 41.5 42.5 -81.5 -80.5

# Export all coordinates to CSV for mapping
python inspect_node_coordinates.py --lake leofs --export-coords leofs_nodes.csv
```

## Using the Python API

### Get Node Coordinate Summary

```python
from src.lake_data_preprocessor import GLOFSDataPreprocessor

preprocessor = GLOFSDataPreprocessor(data_dir="./downloads")

# Get summary of all nodes
node_summary = preprocessor.inspect_nodes(lake="leofs")

print(f"Total nodes: {node_summary['num_nodes']}")
print(f"Lat range: {node_summary['latitude_range']}")
print(f"Lon range: {node_summary['longitude_range']}")
```

### Inspect a Specific Node

```python
# Get detailed info for node #100
node_info = preprocessor.get_node_info(
    lake="leofs",
    node_index=100,
    include_sample_data=True  # Include sample data values
)

print(f"Node {node_info['node_index']}:")
print(f"  Lat: {node_info['latitude']}")
print(f"  Lon: {node_info['longitude']}")
print(f"  Sample data: {node_info['sample_data']}")
```

### Find Nodes in a Geographic Region

```python
# Find nodes in central Lake Erie
result = preprocessor.find_nodes_in_region(
    lake="leofs",
    lat_min=41.5,
    lat_max=42.5,
    lon_min=-81.5,
    lon_max=-80.5
)

print(f"Found {result['num_nodes_in_region']} nodes")
for node in result['node_coordinates'][:5]:
    print(f"  Node {node['node_index']}: ({node['lat']}, {node['lon']})")
```

### Export All Coordinates

```python
import pandas as pd

# Get all coordinates
node_data = preprocessor.inspect_nodes(lake="leofs", output_format="full")

# Create DataFrame
df = pd.DataFrame({
    'node_index': range(len(node_data['lat'])),
    'latitude': node_data['lat'],
    'longitude': node_data['lon']
})

# Save to CSV
df.to_csv('leofs_all_nodes.csv', index=False)
```

## Use Cases

### 1. Creating Maps

Export node coordinates and use them with mapping libraries:

```python
import matplotlib.pyplot as plt

node_data = preprocessor.inspect_nodes(lake="leofs", output_format="full")

plt.scatter(node_data['lon'], node_data['lat'], s=1, alpha=0.5)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Lake Erie FVCOM Mesh Nodes')
plt.savefig('leofs_mesh.png')
```

### 2. Extracting Data for Specific Locations

Find the nearest node to a location of interest:

```python
import numpy as np

# Target location (e.g., Cleveland: 41.5°N, -81.7°W)
target_lat, target_lon = 41.5, -81.7

# Get all coordinates
node_data = preprocessor.inspect_nodes(lake="leofs", output_format="full")
lats = node_data['lat']
lons = node_data['lon']

# Find nearest node
distances = np.sqrt((lats - target_lat)**2 + (lons - target_lon)**2)
nearest_node = np.argmin(distances)

print(f"Nearest node to Cleveland: {nearest_node}")
print(f"Location: ({lats[nearest_node]:.4f}, {lons[nearest_node]:.4f})")

# Extract time series for this node
df = preprocessor.extract_variable_timeseries(
    lake="leofs",
    variable="temp",
    location=(nearest_node,),
    vertical_level=0
)
```

### 3. Regional Analysis

Analyze data for a specific region:

```python
# Define region of interest (e.g., western Lake Erie)
region = preprocessor.find_nodes_in_region(
    lake="leofs",
    lat_min=41.4,
    lat_max=41.9,
    lon_min=-83.5,
    lon_max=-82.5
)

print(f"Western Lake Erie region: {region['num_nodes_in_region']} nodes")

# Extract average temperature for this region
# (You would loop through nodes and average their values)
```

## Lake Geographic Extents

Typical coordinate ranges for each lake:

| Lake | Abbreviation | Latitude Range | Longitude Range |
|------|--------------|----------------|-----------------|
| Lake Erie | leofs | ~41.3°N - 42.9°N | ~-83.5°E - -78.8°E |
| Lake Superior | lsofs | ~46.4°N - 49.0°N | ~-92.1°E - -84.5°E |
| Lake Michigan-Huron | lmhofs | ~41.6°N - 46.0°N | ~-87.9°E - -79.8°E |
| Lake Ontario | loofs | ~43.2°N - 44.3°N | ~-79.8°E - -76.0°E |

Note: Actual ranges depend on the specific FVCOM mesh used.

## Understanding FVCOM Mesh

- **Unstructured mesh**: Nodes are not arranged in a regular grid
- **Node indices**: Sequential integers starting from 0
- **Variable resolution**: More nodes in areas of interest or complex bathymetry
- **Persistent**: Node coordinates are the same across all time steps for a given lake

## Available Methods in GLOFSDataPreprocessor

1. **`inspect_nodes(lake, output_format="summary")`**
   - Get summary or full coordinate data
   - Returns dict with node count and geographic extent

2. **`get_node_coordinates(file_path)`**
   - Extract lat/lon arrays from a NetCDF file
   - Returns dict with coordinate arrays and statistics

3. **`get_node_info(lake, node_index, include_sample_data=False)`**
   - Get detailed info for a specific node
   - Optionally includes sample data values

4. **`find_nodes_in_region(lake, lat_min, lat_max, lon_min, lon_max)`**
   - Find all nodes within geographic bounds
   - Returns node indices and coordinates

## Tips

- **Coordinate system**: GLOFS uses geographic coordinates (latitude/longitude in degrees)
- **Negative longitudes**: Western hemisphere longitudes are negative (e.g., -81.5° for 81.5°W)
- **Data availability**: Make sure you have downloaded NetCDF files before inspecting nodes
- **Mapping tools**: Export coordinates to CSV and use with GIS software, Google Earth, or Python mapping libraries

## Examples

See these files for complete examples:
- `inspect_node_coordinates.py` - Command-line tool
- `quick_start_examples.py` - Example 5 demonstrates node inspection
- `src/lake_data_preprocessor.py` - API documentation in docstrings

## Troubleshooting

**Q: I get "No files found for lake"**
- A: Download data first using `python quick_start_examples.py --example 1`

**Q: How do I know which node index to use?**
- A: Use `find_nodes_in_region()` to find nodes in your area of interest, or export all coordinates and visualize them

**Q: Can I use this with real-time data?**
- A: Yes, as long as you have NetCDF files downloaded. Node coordinates are the same regardless of forecast date.

**Q: What coordinate reference system is used?**
- A: WGS84 geographic coordinates (standard lat/lon in degrees)

## See Also

- [LSTM Variables Guide](LSTM_VARIABLES_GUIDE.md) - Working with surface-level data
- [Quick Start Examples](quick_start_examples.py) - Getting started guide
- [Lake Data Preprocessor](src/lake_data_preprocessor.py) - API documentation
