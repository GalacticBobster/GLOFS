# GLOFS Lake Data Fetcher and LSTM Model

This directory contains Python scripts for fetching Great Lakes Operational Forecast System (GLOFS) data for multiple days and training LSTM models to predict lake variables.

## Overview

The GLOFS system provides operational forecasts for the Great Lakes:
- **LEOFS** - Lake Erie Operational Forecast System
- **LSOFS** - Lake Superior Operational Forecast System
- **LMHOFS** - Lake Michigan-Huron Operational Forecast System
- **LOOFS** - Lake Ontario Operational Forecast System

## Features

1. **Multi-day Data Fetching**: Download GLOFS NetCDF files from AWS S3 for multiple days
2. **Data Preprocessing**: Extract and aggregate lake variables from NetCDF files
3. **LSTM Modeling**: Train LSTM neural networks for time series prediction
4. **Complete Workflow**: End-to-end pipeline from data download to model training

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Required Dependencies

- `boto3` - AWS SDK for downloading data from S3
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `xarray` - NetCDF file handling
- `netCDF4` - NetCDF library
- `tensorflow` - Deep learning framework for LSTM
- `scikit-learn` - Data preprocessing and metrics
- `matplotlib` - Visualization

## Usage

### 1. Fetch Lake Data for Multiple Days

```bash
# Fetch data for Lake Erie from Jan 1-7, 2024
python src/fetch_lake_data_multiday.py \
    --start-date 20240101 \
    --end-date 20240107 \
    --lakes leofs

# Fetch data for all lakes
python src/fetch_lake_data_multiday.py \
    --start-date 20240101 \
    --end-date 20240107

# Fetch specific cycles and forecast steps
python src/fetch_lake_data_multiday.py \
    --start-date 20240101 \
    --end-date 20240103 \
    --lakes leofs lsofs \
    --cycles t00z t12z \
    --forecast-steps 0 1 2 3
```

### 2. Preprocess Data

```python
from src.lake_data_preprocessor import GLOFSDataPreprocessor

# Initialize preprocessor
preprocessor = GLOFSDataPreprocessor(data_dir="../downloads")

# List available files
files = preprocessor.list_files(lake="leofs")

# Inspect variables in a NetCDF file
var_info = preprocessor.inspect_variables(files[0])

# Extract time series for a variable
df = preprocessor.extract_variable_timeseries(
    lake="leofs",
    variable="temp",  # temperature
    aggregation="mean"
)

# Extract multiple variables
df_multi = preprocessor.extract_multiple_variables(
    lake="leofs",
    variables=["temp", "zeta", "u", "v"]  # temp, water level, currents
)

# Prepare data for LSTM
data_dict = preprocessor.prepare_lstm_data(
    df=df,
    target_variable="temp",
    sequence_length=24,
    train_split=0.8
)
```

### 3. Train LSTM Model

```python
from src.lake_lstm_model import train_lstm_model

# Train model with prepared data
model, metrics = train_lstm_model(
    data_dict=data_dict,
    lstm_units=[50, 50],  # Two LSTM layers with 50 units each
    dropout=0.2,
    learning_rate=0.001,
    epochs=100,
    batch_size=32,
    model_save_path="../output/leofs_temp_model.h5",
    plot_save_dir="../output/plots"
)

# Print metrics
print(f"Test RMSE: {metrics['rmse']:.4f}")
print(f"Test R²: {metrics['r2']:.4f}")
```

### 4. Complete Workflow Example

Run the entire workflow from data fetching to model training:

```bash
# Basic usage - fetch 7 days and train model
python src/example_lstm_workflow.py \
    --start-date 20240101 \
    --end-date 20240107 \
    --lake leofs \
    --variable temp

# Advanced usage with custom parameters
python src/example_lstm_workflow.py \
    --start-date 20240101 \
    --end-date 20240131 \
    --lake lsofs \
    --variable zeta \
    --sequence-length 48 \
    --lstm-units 64 64 32 \
    --epochs 150 \
    --batch-size 64 \
    --output-dir ../output/lsofs_experiment
```

## Available Lake Variables

Common variables in GLOFS NetCDF files:

- `temp` - Water temperature (°C)
- `salinity` - Salinity (PSU)
- `zeta` - Water surface elevation (m)
- `u` - Eastward water velocity (m/s)
- `v` - Northward water velocity (m/s)
- `ww` - Vertical water velocity (m/s)

Use the `inspect_variables()` function to see all available variables in your downloaded files.

## File Structure

```
GLOFS/
├── requirements.txt                    # Python dependencies
├── downloads/                          # Downloaded NetCDF files (created automatically)
├── output/                            # Model outputs and plots (created automatically)
└── src/
    ├── fetch_lake_data_multiday.py   # Multi-day data fetcher
    ├── lake_data_preprocessor.py     # Data preprocessing utilities
    ├── lake_lstm_model.py            # LSTM model implementation
    ├── example_lstm_workflow.py      # Complete workflow example
    ├── boto3_glofs.py                # Original single-day fetcher
    └── fetch_glofs.py                # Original NCEI fetcher
```

## Data Sources

- **AWS S3 Bucket**: `s3://noaa-nos-ofs-pds/` (public, no credentials required)
- **NOAA NCEI Archive**: https://www.ncei.noaa.gov/thredds/catalog.html

## Model Architecture

The LSTM model supports:

- Multiple LSTM layers with configurable units
- Dropout for regularization
- Flexible sequence length for input
- Multi-variable input features
- Single-step ahead prediction
- Early stopping to prevent overfitting
- Model checkpointing to save best weights

## Output Files

When running the complete workflow, the following files are generated:

1. **NetCDF Files**: `downloads/*.nc` - Raw GLOFS data
2. **Time Series CSV**: `output/{lake}_{variable}_timeseries.csv` - Extracted time series
3. **Trained Model**: `output/{lake}_{variable}_lstm_model.h5` - Saved LSTM model
4. **Metrics**: `output/{lake}_{variable}_metrics.txt` - Model performance metrics
5. **Plots**:
   - `output/plots/training_history.png` - Training/validation loss and MAE
   - `output/plots/predictions.png` - Actual vs predicted values

## Examples

### Example 1: Quick Test with Minimal Data

```bash
# Fetch 3 days and train with reduced epochs
python src/example_lstm_workflow.py \
    --start-date 20240901 \
    --end-date 20240903 \
    --lake leofs \
    --variable temp \
    --epochs 20
```

### Example 2: Production Training

```bash
# Fetch 30 days and train comprehensive model
python src/example_lstm_workflow.py \
    --start-date 20240101 \
    --end-date 20240131 \
    --lake leofs \
    --variable temp \
    --sequence-length 48 \
    --lstm-units 100 100 50 \
    --epochs 200 \
    --batch-size 64
```

### Example 3: Multiple Variables

```python
from src.lake_data_preprocessor import GLOFSDataPreprocessor

# Extract multiple variables
preprocessor = GLOFSDataPreprocessor()
df = preprocessor.extract_multiple_variables(
    lake="leofs",
    variables=["temp", "zeta", "u", "v"]
)

# Prepare for LSTM with multiple input features
data_dict = preprocessor.prepare_lstm_data(
    df=df,
    target_variable="temp",
    feature_variables=["temp", "zeta", "u", "v"],
    sequence_length=24
)

# Train model
from src.lake_lstm_model import train_lstm_model
model, metrics = train_lstm_model(data_dict, epochs=100)
```

## Tips

1. **Data Volume**: Each NetCDF file is typically 10-50 MB. Plan storage accordingly.
2. **Missing Data**: The fetcher will skip files that don't exist on S3.
3. **Sequence Length**: Typical values are 24 (1 day), 48 (2 days), or 168 (1 week).
4. **Training Time**: GPU is recommended for training. CPU training may take significantly longer.
5. **Memory**: Large datasets may require significant RAM. Consider processing in chunks if needed.

## Troubleshooting

### Issue: Files not downloading
- Check date range - data may not be available for all dates
- Verify lake name spelling
- Check internet connection

### Issue: Variable not found
- Use `inspect_variables()` to see available variables in your files
- Variable names may differ between lakes

### Issue: Not enough data for LSTM
- Increase date range to fetch more data
- Reduce sequence length
- Check for missing files in downloads directory

### Issue: TensorFlow errors
- Ensure TensorFlow is installed: `pip install tensorflow`
- Check TensorFlow version compatibility with your Python version

## License

See LICENSE file in the repository root.

## References

- [NOAA Great Lakes Operational Forecast System](https://oceanservice.noaa.gov/observations/glofs/)
- [NOAA Open Data Dissemination (NODD)](https://www.noaa.gov/information-technology/open-data-dissemination)
- [LSTM Networks](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
