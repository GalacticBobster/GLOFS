"""
LSTM model for lake variable prediction.

This module provides an LSTM-based time series forecasting model
for Great Lakes operational forecast variables.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Optional, Tuple
import os
import json

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Install with: pip install tensorflow")


class LakeLSTMModel:
    """LSTM model for lake variable prediction."""
    
    def __init__(self, sequence_length: int = 24, n_features: int = 1):
        """
        Initialize the LSTM model.
        
        Args:
            sequence_length: Length of input sequences
            n_features: Number of input features
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LakeLSTMModel")
        
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.history = None
        
    def build_model(self, lstm_units: list = [50, 50], 
                   dropout: float = 0.2,
                   learning_rate: float = 0.001) -> None:
        """
        Build the LSTM model architecture.
        
        Args:
            lstm_units: List of units for each LSTM layer
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        self.model = Sequential()
        
        # First LSTM layer
        self.model.add(LSTM(
            units=lstm_units[0],
            return_sequences=len(lstm_units) > 1,
            input_shape=(self.sequence_length, self.n_features)
        ))
        self.model.add(Dropout(dropout))
        
        # Additional LSTM layers
        for i, units in enumerate(lstm_units[1:]):
            return_seq = i < len(lstm_units) - 2
            self.model.add(LSTM(units=units, return_sequences=return_seq))
            self.model.add(Dropout(dropout))
        
        # Output layer
        self.model.add(Dense(units=1))
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
             epochs: int = 100, batch_size: int = 32,
             early_stopping_patience: int = 10,
             model_checkpoint_path: Optional[str] = None) -> Dict:
        """
        Train the LSTM model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            epochs: Number of training epochs
            batch_size: Batch size
            early_stopping_patience: Patience for early stopping
            model_checkpoint_path: Path to save best model
            
        Returns:
            Dictionary with training history
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        callbacks = []
        
        # Early stopping
        callbacks.append(EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=early_stopping_patience,
            restore_best_weights=True,
            verbose=1
        ))
        
        # Model checkpoint
        if model_checkpoint_path:
            os.makedirs(os.path.dirname(model_checkpoint_path), exist_ok=True)
            callbacks.append(ModelCheckpoint(
                filepath=model_checkpoint_path,
                monitor='val_loss' if X_val is not None else 'loss',
                save_best_only=True,
                verbose=1
            ))
        
        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return {
            "loss": self.history.history['loss'],
            "mae": self.history.history['mae'],
            "val_loss": self.history.history.get('val_loss', []),
            "val_mae": self.history.history.get('val_mae', [])
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not built or loaded.")
        
        return self.model.predict(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            X_test: Test features
            y_test: Test targets
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not built or loaded.")
        
        # Make predictions
        y_pred = self.predict(X_test).flatten()
        
        # Calculate metrics
        mse = np.mean((y_test - y_pred) ** 2)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(mse)
        
        # R-squared
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            "mse": mse,
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        }
    
    def plot_training_history(self, save_path: Optional[str] = None) -> None:
        """
        Plot training history.
        
        Args:
            save_path: Path to save plot (optional)
        """
        if self.history is None:
            print("No training history available.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot loss
        axes[0].plot(self.history.history['loss'], label='Train Loss')
        if 'val_loss' in self.history.history:
            axes[0].plot(self.history.history['val_loss'], label='Val Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Model Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # Plot MAE
        axes[1].plot(self.history.history['mae'], label='Train MAE')
        if 'val_mae' in self.history.history:
            axes[1].plot(self.history.history['val_mae'], label='Val MAE')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('MAE')
        axes[1].set_title('Model MAE')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_predictions(self, y_true: np.ndarray, y_pred: np.ndarray,
                        timestamps: Optional[pd.DatetimeIndex] = None,
                        variable_name: str = "Variable",
                        save_path: Optional[str] = None) -> None:
        """
        Plot predictions vs actual values.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            timestamps: Optional timestamps for x-axis
            variable_name: Name of the variable being predicted
            save_path: Path to save plot (optional)
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Time series plot
        if timestamps is not None:
            axes[0].plot(timestamps, y_true, label='Actual', alpha=0.7)
            axes[0].plot(timestamps, y_pred, label='Predicted', alpha=0.7)
            axes[0].set_xlabel('Time')
        else:
            axes[0].plot(y_true, label='Actual', alpha=0.7)
            axes[0].plot(y_pred, label='Predicted', alpha=0.7)
            axes[0].set_xlabel('Sample')
        
        axes[0].set_ylabel(variable_name)
        axes[0].set_title(f'{variable_name} - Actual vs Predicted')
        axes[0].legend()
        axes[0].grid(True)
        
        # Scatter plot
        axes[1].scatter(y_true, y_pred, alpha=0.5)
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        axes[1].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        axes[1].set_xlabel('Actual')
        axes[1].set_ylabel('Predicted')
        axes[1].set_title('Prediction Scatter Plot')
        axes[1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Predictions plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def save_model(self, path: str) -> None:
        """
        Save model to disk.
        
        Args:
            path: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save.")
        
        self.model.save(path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """
        Load model from disk.
        
        Args:
            path: Path to load model from
        """
        self.model = keras.models.load_model(path)
        print(f"Model loaded from {path}")


def train_lstm_model(data_dict: Dict, 
                    lstm_units: list = [50, 50],
                    dropout: float = 0.2,
                    learning_rate: float = 0.001,
                    epochs: int = 100,
                    batch_size: int = 32,
                    early_stopping_patience: int = 10,
                    model_save_path: Optional[str] = None,
                    plot_save_dir: Optional[str] = None) -> Tuple[LakeLSTMModel, Dict]:
    """
    Train an LSTM model using prepared data.
    
    Args:
        data_dict: Dictionary from prepare_lstm_data
        lstm_units: List of units for each LSTM layer
        dropout: Dropout rate
        learning_rate: Learning rate
        epochs: Number of epochs
        batch_size: Batch size
        early_stopping_patience: Early stopping patience
        model_save_path: Path to save model
        plot_save_dir: Directory to save plots
        
    Returns:
        Trained model and evaluation metrics
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for training LSTM models")
    
    # Extract data
    X_train = data_dict["X_train"]
    y_train = data_dict["y_train"]
    X_test = data_dict["X_test"]
    y_test = data_dict["y_test"]
    
    # Get dimensions
    sequence_length = data_dict["sequence_length"]
    n_features = X_train.shape[2]
    
    # Build model
    model = LakeLSTMModel(sequence_length=sequence_length, n_features=n_features)
    model.build_model(lstm_units=lstm_units, dropout=dropout, learning_rate=learning_rate)
    
    print(f"\nModel Summary:")
    model.model.summary()
    
    # Split training data into train and validation (80/20 split of training data)
    val_split_idx = int(len(X_train) * 0.8)
    X_train_final = X_train[:val_split_idx]
    y_train_final = y_train[:val_split_idx]
    X_val = X_train[val_split_idx:]
    y_val = y_train[val_split_idx:]
    
    # Train model
    print(f"\nTraining model...")
    print(f"Training samples: {len(X_train_final)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    
    history = model.train(
        X_train_final, y_train_final,
        X_val=X_val, y_val=y_val,
        epochs=epochs,
        batch_size=batch_size,
        early_stopping_patience=early_stopping_patience,
        model_checkpoint_path=model_save_path
    )
    
    # Evaluate model
    print(f"\nEvaluating model on test set...")
    metrics = model.evaluate(X_test, y_test)
    print(f"\nTest Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Save plots
    if plot_save_dir:
        os.makedirs(plot_save_dir, exist_ok=True)
        
        # Training history plot
        model.plot_training_history(
            save_path=os.path.join(plot_save_dir, "training_history.png")
        )
        
        # Predictions plot
        y_pred = model.predict(X_test).flatten()
        model.plot_predictions(
            y_test, y_pred,
            variable_name=data_dict["target_variable"],
            save_path=os.path.join(plot_save_dir, "predictions.png")
        )
    
    # Save model
    if model_save_path:
        model.save_model(model_save_path)
    
    return model, metrics


def main():
    """Example usage of the LSTM model."""
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow not available. Cannot run example.")
        return
    
    # Create dummy data for demonstration
    sequence_length = 24
    n_samples = 1000
    n_features = 3
    
    X_train = np.random.randn(n_samples, sequence_length, n_features)
    y_train = np.random.randn(n_samples)
    X_test = np.random.randn(200, sequence_length, n_features)
    y_test = np.random.randn(200)
    
    data_dict = {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "sequence_length": sequence_length,
        "target_variable": "example_var"
    }
    
    # Train model
    model, metrics = train_lstm_model(
        data_dict,
        lstm_units=[32, 32],
        epochs=10,
        batch_size=32
    )
    
    print("\nExample training completed!")


if __name__ == "__main__":
    main()
