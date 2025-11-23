# LSTM Variables for 3D Lake Data - Implementation Guide

## Overview

This guide explains how to extract variables from 3D Great Lakes data for training 2D LSTM time series models.

## The Challenge

**Question**: "What variables are being written for LSTM? Each of the lakes are 3-dimensional lakes, so how do we create custom surface level temperatures for 2-D LSTM?"

**Answer**: Great Lakes data is 3-dimensional (spatial x, y + vertical depth + time), but LSTM models work with 2D time series (features × time). We extract **surface-level** data from 3D variables to create appropriate input for LSTM models.

## Variable Types in GLOFS Data

### 3D Variables (with vertical structure)
These variables have dimensions: `(time, siglay, node)`
- `temp` - Water temperature (°C)
- `salinity` - Salinity (PSU)
- `u` - Eastward velocity (m/s)
- `v` - Northward velocity (m/s)
- `ww` - Vertical velocity (m/s)

Where:
- `siglay` = vertical layer index (0 = surface, higher = deeper)
- `node` = spatial location in unstructured FVCOM mesh

### 2D Variables (surface only or depth-integrated)
These variables have dimensions: `(time, node)`
- `zeta` - Water surface elevation (m)
- `ua` - Depth-averaged eastward velocity (m/s)
- `va` - Depth-averaged northward velocity (m/s)

## How to Extract Surface-Level Data for LSTM

### Method 1: Use the Convenience Method (Recommended)

```python
from src.lake_data_preprocessor import GLOFSDataPreprocessor

preprocessor = GLOFSDataPreprocessor()

# Extract surface temperature (easiest way)
df = preprocessor.extract_surface_temperature(
    lake="leofs",  # Lake Erie
    aggregation="mean"  # Spatial average
)
```

### Method 2: Use vertical_level Parameter

```python
# Extract surface temperature explicitly
df = preprocessor.extract_variable_timeseries(
    lake="leofs",
    variable="temp",
    vertical_level=0,  # 0 = surface layer
    aggregation="mean"
)

# Extract other surface variables
df_u = preprocessor.extract_variable_timeseries(
    lake="leofs",
    variable="u",  # Eastward velocity
    vertical_level=0,
    aggregation="mean"
)
```

### Method 3: Use "surface" Aggregation Shorthand

```python
# "surface" is a convenience shorthand for vertical_level=0
df = preprocessor.extract_variable_timeseries(
    lake="leofs",
    variable="temp",
    aggregation="surface"  # Automatically uses vertical_level=0
)
```

### Method 4: Command-Line Flag (Easy for Scripts)

```bash
# Use --surface-level flag for surface extraction
python src/example_lstm_workflow.py \
    --start-date 20240101 \
    --end-date 20240107 \
    --lake leofs \
    --variable temp \
    --surface-level
```

## Multi-Variable LSTM Input

Extract multiple surface variables for LSTM models:

```python
# Extract multiple surface-level variables
df = preprocessor.extract_multiple_variables(
    lake="leofs",
    variables=["temp", "u", "v"],  # Surface temp and currents
    vertical_level=0,  # Surface layer for all 3D variables
    aggregation="mean"
)

# Prepare for LSTM
data_dict = preprocessor.prepare_lstm_data(
    df=df,
    target_variable="temp",
    feature_variables=["temp", "u", "v"],
    sequence_length=24
)

# Train model
from src.lake_lstm_model import train_lstm_model
model, metrics = train_lstm_model(data_dict, epochs=100)
```

## Lake Name Abbreviations

- `leofs` = Lake Erie Operational Forecast System
- `lsofs` = Lake Superior Operational Forecast System
- `lmhofs` = Lake Michigan-Huron Operational Forecast System
- `loofs` = Lake Ontario Operational Forecast System

## When to Use Surface vs Depth-Averaged

### Use Surface-Level (vertical_level=0) when:
- ✅ Predicting surface conditions (ice formation, temperature)
- ✅ Weather-related forecasts (surface interacts with atmosphere)
- ✅ Navigation safety (ships care about surface conditions)
- ✅ Training simpler, faster LSTM models
- ✅ **Recommended for most LSTM applications**

### Use Depth-Averaged (no vertical_level) when:
- ⚠️ Modeling whole water column behavior
- ⚠️ When vertical stratification is not important
- ⚠️ Comparing with depth-integrated measurements

## Complete Example

```python
from src.lake_data_preprocessor import GLOFSDataPreprocessor
from src.lake_lstm_model import train_lstm_model
import os

# Initialize preprocessor
preprocessor = GLOFSDataPreprocessor(data_dir="../downloads")

# Extract surface temperature time series
df = preprocessor.extract_surface_temperature(
    lake="leofs",
    aggregation="mean"
)

print(f"Extracted {len(df)} time steps")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Prepare for LSTM
data_dict = preprocessor.prepare_lstm_data(
    df=df,
    target_variable="temp",
    sequence_length=24,
    train_split=0.8
)

# Train model
model, metrics = train_lstm_model(
    data_dict=data_dict,
    lstm_units=[50, 50],
    epochs=100,
    batch_size=32,
    model_save_path="../output/leofs_surface_temp_model.h5",
    plot_save_dir="../output/plots"
)

print(f"Test RMSE: {metrics['rmse']:.4f}")
print(f"Test R²: {metrics['r2']:.4f}")
```

## Variables Written for LSTM

| Variable | Dimension | Extract Method | LSTM Input | Purpose |
|----------|-----------|----------------|------------|---------|
| temp (surface) | 3D→2D | vertical_level=0 | ✅ Primary | Surface water temperature |
| salinity (surface) | 3D→2D | vertical_level=0 | ✅ Optional | Surface salinity |
| u (surface) | 3D→2D | vertical_level=0 | ✅ Optional | Surface eastward velocity |
| v (surface) | 3D→2D | vertical_level=0 | ✅ Optional | Surface northward velocity |
| zeta | 2D | (no vertical_level) | ✅ Primary | Water surface elevation |
| ua | 2D | (no vertical_level) | ✅ Optional | Depth-averaged velocity |
| va | 2D | (no vertical_level) | ✅ Optional | Depth-averaged velocity |

## Technical Details

### How It Works
1. **Detection**: Code checks for 'siglay' or 'siglev' dimensions to identify 3D variables
2. **Extraction**: Uses `numpy.take(data, 0, axis=vert_dim_idx)` to extract surface layer
3. **Aggregation**: Then spatially aggregates (mean/max/min) across all nodes
4. **Output**: Single time series value per time step

### Error Handling
- ✅ Warns if vertical_level exceeds available layers
- ✅ Warns if location index is out of bounds
- ✅ Handles missing vertical dimensions gracefully
- ✅ Uses informative messages for debugging

### Backward Compatibility
- ✅ All existing code continues to work
- ✅ Default behavior unchanged (depth-averaged)
- ✅ New parameters are optional

## Troubleshooting

**Q: My LSTM is not training well**
- A: Try using surface-level data instead of depth-averaged: `vertical_level=0`

**Q: Which aggregation method should I use?**
- A: Use `aggregation="mean"` for most cases (spatially averaged surface temperature)

**Q: Can I use multiple depth levels?**
- A: Yes, but you'd need to extract each level separately and concatenate them as different features

**Q: What if I want data at a specific location?**
- A: Use the `location` parameter with a node index (requires knowledge of FVCOM mesh structure)

## See Also

- `src/README_LSTM.md` - Complete LSTM documentation
- `src/lake_data_preprocessor.py` - Preprocessor implementation
- `src/example_lstm_workflow.py` - End-to-end workflow example
- `quick_start_examples.py` - Quick start guide
