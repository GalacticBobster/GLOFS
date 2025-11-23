# GLOFS
Scripts for retrieving FVCOM Great Lakes data products and remapping on FV3 grid

## Overview

This repository contains tools for working with Great Lakes Operational Forecast System (GLOFS) data:

- **Data Fetching**: Download GLOFS data from NOAA archives (NCEI and AWS S3)
- **Data Processing**: Extract and preprocess lake variables from NetCDF files
- **Machine Learning**: Train LSTM models for lake variable prediction with surface-level data extraction
- **Grid Remapping**: Remap FVCOM data to FV3 grid

## Quick Start

### Fetch Lake Data and Train LSTM Models (NEW!)

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick start examples
python quick_start_examples.py

# Or run the complete workflow with surface-level extraction
python src/example_lstm_workflow.py \
    --start-date 20240101 \
    --end-date 20240107 \
    --lake leofs \
    --variable temp \
    --surface-level
```

**Documentation:**
- [Node Coordinates Guide](NODE_COORDINATES_GUIDE.md) - **NEW!** Inspect node lat/lon coordinates for mapping
- [LSTM Variables Guide](LSTM_VARIABLES_GUIDE.md) - How to extract surface-level data from 3D lakes for LSTM
- [src/README_LSTM.md](src/README_LSTM.md) - Detailed LSTM functionality documentation

## Repository Structure

### Data Fetching Scripts
- `fetch_glofs.py` - Fetch GLOFS data from NOAA NCEI archive for all Great Lakes (single day)
- `fetch_lake_data_multiday.py` - **NEW!** Fetch GLOFS data for multiple days from AWS S3
- `boto3_glofs.py` - Fetch data from AWS S3 using boto3 (single day)
- `fetch_RAP.py` - Fetch all RAP forecast data from AWS

### Data Processing & ML
- `lake_data_preprocessor.py` - Extract and preprocess lake variables from NetCDF files
- `lake_lstm_model.py` - LSTM neural network for time series prediction
- `example_lstm_workflow.py` - Complete end-to-end workflow example
- `quick_start_examples.py` - Quick start guide with examples
- `inspect_node_coordinates.py` - **NEW!** Inspect node lat/lon coordinates for mapping

### Grid Remapping Scripts
- `sfc_extract.csh` - Extract only the surface layer from FVCOM data
- `stitch_all.csh` - Stitch all the surface layer for each lake
- `interp_skintemp_5lakes_ice_fv3grid_ver7_GLcropped.py` - Combine all Great Lakes mask files and stitch them together

## Features

### Node Coordinate Inspection (NEW!)
- Extract latitude/longitude coordinates for all nodes
- Find nodes within geographic regions
- Inspect specific node locations
- Export coordinates to CSV for mapping/GIS

### Multi-Day Data Fetching
- Download GLOFS data for date ranges
- Support for all Great Lakes (LEOFS, LSOFS, LMHOFS, LOOFS)
- Automatic handling of cycles and forecast steps
- Progress tracking and statistics

### LSTM Time Series Prediction
- Extract lake variables (temperature, water level, currents, etc.)
- Preprocess time series data with proper scaling
- Train customizable LSTM models
- Visualize training history and predictions
- Comprehensive evaluation metrics

## Installation

```bash
# Clone the repository
git clone https://github.com/GalacticBobster/GLOFS.git
cd GLOFS

# Install Python dependencies
pip install -r requirements.txt
```

## Documentation

- **[Node Coordinates Guide](NODE_COORDINATES_GUIDE.md)** - Inspect node lat/lon coordinates for mapping and geographic analysis
- **[LSTM Variables Guide](LSTM_VARIABLES_GUIDE.md)** - How to extract surface-level data from 3D lakes for LSTM models
- [LSTM Model Documentation](src/README_LSTM.md) - Comprehensive guide for LSTM functionality
- See individual script files for specific usage instructions

## Available Lakes

- **LEOFS** - Lake Erie Operational Forecast System
- **LSOFS** - Lake Superior Operational Forecast System
- **LMHOFS** - Lake Michigan-Huron Operational Forecast System
- **LOOFS** - Lake Ontario Operational Forecast System

## License

See [LICENSE](LICENSE) file for details.

