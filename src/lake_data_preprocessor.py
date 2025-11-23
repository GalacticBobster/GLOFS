"""
Data preprocessing module for GLOFS NetCDF files.

This module extracts and prepares lake variables for LSTM modeling.
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import glob


class GLOFSDataPreprocessor:
    """Preprocess GLOFS NetCDF data for LSTM modeling."""
    
    def __init__(self, data_dir: str = "../downloads"):
        """
        Initialize the preprocessor.
        
        Args:
            data_dir: Directory containing NetCDF files
        """
        self.data_dir = data_dir
        self.available_variables = None
        
    def list_files(self, lake: Optional[str] = None, 
                   pattern: str = "*.nc") -> List[str]:
        """
        List available NetCDF files.
        
        Args:
            lake: Specific lake to filter (e.g., "leofs")
            pattern: File pattern to match
            
        Returns:
            List of file paths
        """
        if lake:
            pattern = f"{lake}.*.nc"
        
        files = glob.glob(os.path.join(self.data_dir, pattern))
        return sorted(files)
    
    def load_netcdf(self, file_path: str) -> xr.Dataset:
        """
        Load a NetCDF file.
        
        Args:
            file_path: Path to NetCDF file
            
        Returns:
            xarray Dataset
        """
        try:
            ds = xr.open_dataset(file_path)
            return ds
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def inspect_variables(self, file_path: str) -> Dict:
        """
        Inspect variables in a NetCDF file.
        
        Args:
            file_path: Path to NetCDF file
            
        Returns:
            Dictionary with variable information
        """
        ds = self.load_netcdf(file_path)
        if ds is None:
            return {}
        
        var_info = {}
        for var_name in ds.data_vars:
            var = ds[var_name]
            var_info[var_name] = {
                "dims": var.dims,
                "shape": var.shape,
                "dtype": str(var.dtype),
                "attrs": dict(var.attrs)
            }
        
        ds.close()
        return var_info
    
    def extract_variable_timeseries(self, lake: str, variable: str,
                                   location: Optional[Tuple[int, int]] = None,
                                   aggregation: str = "mean",
                                   vertical_level: Optional[int] = None) -> pd.DataFrame:
        """
        Extract time series for a specific variable across multiple files.
        
        For 3D variables (temp, salinity, u, v, ww):
        - These have dimensions (time, siglay, node) where siglay is the vertical layer
        - Use vertical_level=0 for surface-level data (recommended for LSTM models)
        - Use aggregation="mean" without vertical_level to average across all vertical levels
        - The method detects 3D variables by checking for 'siglay' or 'siglev' dimensions
        
        For 2D variables (zeta, ua, va):
        - These have dimensions (time, node) - no vertical dimension
        - vertical_level parameter is ignored
        
        Args:
            lake: Lake name (e.g., "leofs")
            variable: Variable name (e.g., "temp", "zeta", "u", "v")
            location: Optional (node_index,) or node index for spatial extraction.
                     FVCOM uses unstructured mesh with node-based indexing.
                     If not specified, spatial aggregation is performed.
            aggregation: Aggregation method ("mean", "max", "min", "surface").
                        "surface" is equivalent to vertical_level=0 for 3D variables.
            vertical_level: Optional vertical level index for 3D variables.
                           0 = surface (top layer), higher values = deeper layers.
                           If specified, extracts only that vertical level before spatial aggregation.
            
        Returns:
            DataFrame with time series data
        """
        # Validate aggregation parameter
        valid_aggregations = ["mean", "max", "min", "surface"]
        if aggregation not in valid_aggregations:
            print(f"Warning: Invalid aggregation '{aggregation}'. Using 'mean' instead.")
            aggregation = "mean"
        
        # Handle "surface" aggregation as vertical_level=0
        if aggregation == "surface":
            vertical_level = 0
            aggregation = "mean"  # Use mean for spatial aggregation
        
        files = self.list_files(lake=lake)
        
        if not files:
            print(f"No files found for lake {lake}")
            return pd.DataFrame()
        
        data = []
        timestamps = []
        
        for file_path in files:
            try:
                ds = self.load_netcdf(file_path)
                if ds is None or variable not in ds.data_vars:
                    continue
                
                # Extract timestamp from filename
                # Format: lake.cycle.YYYYMMDD.fields.nXXX.nc
                filename = os.path.basename(file_path)
                parts = filename.split('.')
                date_str = parts[2]  # YYYYMMDD
                cycle = parts[1]  # t00z, t06z, etc.
                forecast_step = parts[-2]  # nXXX
                
                # Parse date and cycle
                date = datetime.strptime(date_str, "%Y%m%d")
                hour = int(cycle[1:3])  # Extract hour from cycle
                step = int(forecast_step[1:])  # Extract step number
                
                # Create timestamp
                timestamp = date.replace(hour=hour) + pd.Timedelta(hours=step)
                
                # Extract variable data
                var_data_obj = ds[variable]
                var_data = var_data_obj.values
                
                # Check if this is a 3D variable by examining dimensions
                # 3D variables have 'siglay' or 'siglev' dimension (vertical layers)
                # 2D variables only have 'node' or spatial dimensions
                var_dims = var_data_obj.dims if hasattr(var_data_obj, 'dims') else []
                is_3d = 'siglay' in var_dims or 'siglev' in var_dims
                
                # Extract surface level for 3D variables if specified
                if vertical_level is not None and is_3d:
                    # Find the vertical dimension index
                    if 'siglay' in var_dims:
                        vert_dim_idx = var_dims.index('siglay')
                    elif 'siglev' in var_dims:
                        vert_dim_idx = var_dims.index('siglev')
                    else:
                        vert_dim_idx = 0  # Fallback
                    
                    # Extract specific vertical level (0 = surface)
                    if vertical_level < var_data.shape[vert_dim_idx]:
                        # Use numpy's take to extract along the correct axis
                        var_data = np.take(var_data, vertical_level, axis=vert_dim_idx)
                    else:
                        print(f"Warning: vertical_level {vertical_level} exceeds available levels {var_data.shape[vert_dim_idx]}. Using surface level.")
                        var_data = np.take(var_data, 0, axis=vert_dim_idx)
                
                # Handle different dimensions for location-based extraction
                if location is not None:
                    # Convert location to node index if it's a tuple
                    node_idx = location[0] if isinstance(location, (tuple, list)) else location
                    
                    # After vertical level extraction, 3D becomes 2D: (node,)
                    # 2D variables are already: (node,)
                    if len(var_data.shape) == 1:
                        # 1D array (node dimension only)
                        if node_idx < len(var_data):
                            value = var_data[node_idx]
                        else:
                            print(f"Warning: location index {node_idx} exceeds array size {len(var_data)}. Using spatial mean instead.")
                            value = np.nanmean(var_data)
                    elif len(var_data.shape) >= 2:
                        # Multi-dimensional - still has vertical or time dimensions
                        # This happens if vertical_level wasn't specified for a 3D variable
                        # Take mean over all non-spatial dimensions, then extract location
                        var_data_flat = np.nanmean(var_data, axis=tuple(range(len(var_data.shape) - 1)))
                        if node_idx < len(var_data_flat):
                            value = var_data_flat[node_idx]
                        else:
                            print(f"Warning: location index {node_idx} exceeds array size. Using spatial mean instead.")
                            value = np.nanmean(var_data)
                    else:
                        # Scalar value
                        value = var_data
                else:
                    # Aggregate over spatial dimensions
                    if aggregation == "mean":
                        value = np.nanmean(var_data)
                    elif aggregation == "max":
                        value = np.nanmax(var_data)
                    elif aggregation == "min":
                        value = np.nanmin(var_data)
                    else:
                        # Should not reach here due to validation above
                        value = np.nanmean(var_data)
                
                data.append(value)
                timestamps.append(timestamp)
                
                ds.close()
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame({
            "timestamp": timestamps,
            variable: data
        })
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        return df
    
    def extract_surface_temperature(self, lake: str,
                                    location: Optional[Tuple[int, int]] = None,
                                    aggregation: str = "mean") -> pd.DataFrame:
        """
        Convenience method to extract surface-level temperature for LSTM models.
        
        This extracts the surface layer (vertical_level=0) from the 3D temperature data,
        which is the recommended approach for training LSTM models on lake surface conditions.
        
        Args:
            lake: Lake name (e.g., "leofs")
            location: Optional (x, y) location indices for spatial extraction
            aggregation: Spatial aggregation method ("mean", "max", "min")
            
        Returns:
            DataFrame with surface temperature time series
            
        Example:
            >>> preprocessor = GLOFSDataPreprocessor()
            >>> df = preprocessor.extract_surface_temperature("leofs", aggregation="mean")
            >>> # Returns spatially-averaged surface temperature over time
        """
        return self.extract_variable_timeseries(
            lake=lake,
            variable="temp",
            location=location,
            aggregation=aggregation,
            vertical_level=0
        )
    
    def extract_multiple_variables(self, lake: str, variables: List[str],
                                   location: Optional[Tuple[int, int]] = None,
                                   aggregation: str = "mean",
                                   vertical_level: Optional[int] = None) -> pd.DataFrame:
        """
        Extract time series for multiple variables.
        
        Args:
            lake: Lake name
            variables: List of variable names
            location: Optional (x, y) location indices
            aggregation: Aggregation method
            vertical_level: Optional vertical level index for 3D variables (0=surface)
            
        Returns:
            DataFrame with time series for all variables
        """
        dfs = []
        
        for var in variables:
            df = self.extract_variable_timeseries(
                lake, var, location, aggregation, vertical_level
            )
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        # Merge all dataframes on timestamp
        result = dfs[0]
        for df in dfs[1:]:
            result = pd.merge(result, df, on="timestamp", how="outer")
        
        result = result.sort_values("timestamp").reset_index(drop=True)
        
        return result
    
    def prepare_lstm_data(self, df: pd.DataFrame, 
                         target_variable: str,
                         feature_variables: Optional[List[str]] = None,
                         sequence_length: int = 24,
                         train_split: float = 0.8) -> Dict:
        """
        Prepare data for LSTM training.
        
        Args:
            df: DataFrame with time series data
            target_variable: Variable to predict
            feature_variables: Variables to use as features (default: all except target)
            sequence_length: Length of input sequences
            train_split: Proportion of data for training
            
        Returns:
            Dictionary with train/test data and scalers
        """
        from sklearn.preprocessing import MinMaxScaler
        
        # Select features
        if feature_variables is None:
            feature_variables = [col for col in df.columns if col not in ["timestamp", target_variable]]
        
        # Ensure target variable is in dataframe
        if target_variable not in df.columns:
            raise ValueError(f"Target variable {target_variable} not found in dataframe")
        
        # Add target to features if not already there
        all_features = feature_variables + [target_variable]
        # Remove duplicates while preserving order (dict.fromkeys maintains insertion order in Python 3.7+)
        all_features = list(dict.fromkeys(all_features))
        
        # Extract data
        data = df[all_features].values
        
        # Handle missing values
        if np.isnan(data).any():
            print("Warning: NaN values detected. Filling with forward fill and mean.")
            df_clean = df[all_features].ffill().fillna(df[all_features].mean())
            data = df_clean.values
        
        # Scale data
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(len(data_scaled) - sequence_length):
            X.append(data_scaled[i:i+sequence_length, :])
            # Target is the last feature
            target_idx = all_features.index(target_variable)
            y.append(data_scaled[i+sequence_length, target_idx])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split into train and test
        split_idx = int(len(X) * train_split)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "scaler": scaler,
            "feature_names": all_features,
            "target_variable": target_variable,
            "sequence_length": sequence_length
        }


def main():
    """Example usage of the preprocessor."""
    preprocessor = GLOFSDataPreprocessor()
    
    # List available files
    files = preprocessor.list_files(lake="leofs")
    print(f"Found {len(files)} files for leofs")
    
    if files:
        # Inspect first file
        print("\nInspecting first file:")
        var_info = preprocessor.inspect_variables(files[0])
        print("\nAvailable variables:")
        for var_name, info in var_info.items():
            print(f"  {var_name}: {info['shape']}")


if __name__ == "__main__":
    main()
