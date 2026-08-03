"""Demand Forecasting Module - XGBoost-based demand prediction.

This module provides OOP-based demand forecasting using XGBoost,
optimized for Indian e-commerce patterns.

Classes:
    ModelConfig: Configuration for model training
    ModelMetrics: Performance metrics container
    DemandForecaster: Main forecasting class
"""

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
import xgboost as xgb

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for XGBoost model training."""
    
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0.01
    reg_lambda: float = 1.0
    random_state: int = 42
    test_size: float = 0.2
    early_stopping_rounds: int = 10


@dataclass
class ModelMetrics:
    """Container for model performance metrics."""
    
    rmse: float
    r2_score: float
    mape: float
    n_samples: int
    n_features: int
    
    def __str__(self) -> str:
        return (
            f"RMSE: ₹{self.rmse:.2f} | "
            f"R²: {self.r2_score:.4f} | "
            f"MAPE: {self.mape:.2f}%"
        )


class DemandForecaster:
    """XGBoost-based demand forecasting model.
    
    Handles model training, predictions, and evaluation for
    Indian e-commerce demand forecasting.
    
    Attributes:
        config: ModelConfig instance
        model: Trained XGBoost model
        scaler: StandardScaler for feature normalization
        feature_names: List of feature names
    """
    
    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        model_dir: Optional[Path | str] = None
    ):
        """Initialize DemandForecaster.
        
        Args:
            config: Optional ModelConfig (uses defaults if None)
            model_dir: Directory for saving/loading models
        """
        self.config = config or ModelConfig()
        self.model_dir = (
            Path(model_dir) if model_dir
            else Path.home() / ".cache" / "twinai_models"
        )
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model: Optional[xgb.XGBRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: Optional[list] = None
        
        logger.info(f"DemandForecaster initialized")
    
    def _create_model(self) -> xgb.XGBRegressor:
        """Create XGBoost model with configured parameters.
        
        Returns:
            Configured XGBRegressor instance
        """
        return xgb.XGBRegressor(
            n_estimators=self.config.n_estimators,
            max_depth=self.config.max_depth,
            learning_rate=self.config.learning_rate,
            subsample=self.config.subsample,
            colsample_bytree=self.config.colsample_bytree,
            reg_alpha=self.config.reg_alpha,
            reg_lambda=self.config.reg_lambda,
            random_state=self.config.random_state,
            tree_method="hist",
            verbose=0
        )
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        verbose: bool = True
    ) -> ModelMetrics:
        """Train demand forecasting model.
        
        Args:
            X_train: Feature DataFrame
            y_train: Target Series
            verbose: Print training metrics
            
        Returns:
            ModelMetrics object with performance metrics
            
        Raises:
            ValueError: If training data is empty
        """
        if len(X_train) == 0 or len(y_train) == 0:
            raise ValueError("Training data cannot be empty")
        
        logger.info(f"Starting training on {len(X_train)} samples")
        
        # Store feature names
        self.feature_names = X_train.columns.tolist()
        
        # Split data
        X_tr, X_te, y_tr, y_te = train_test_split(
            X_train, y_train,
            test_size=self.config.test_size,
            random_state=self.config.random_state
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_tr_scaled = self.scaler.fit_transform(X_tr)
        X_te_scaled = self.scaler.transform(X_te)
        
        # Create and train model
        self.model = self._create_model()
        self.model.fit(
            X_tr_scaled, y_tr,
            eval_set=[(X_te_scaled, y_te)],
            early_stopping_rounds=self.config.early_stopping_rounds,
            verbose=False
        )
        
        # Calculate metrics
        y_pred = self.model.predict(X_te_scaled)
        
        rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))
        r2 = float(r2_score(y_te, y_pred))
        mape = float(mean_absolute_percentage_error(y_te, y_pred)) * 100
        
        metrics = ModelMetrics(
            rmse=rmse,
            r2_score=r2,
            mape=mape,
            n_samples=len(X_train),
            n_features=X_train.shape[1]
        )
        
        if verbose:
            logger.info(f"Training complete: {metrics}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict demand for new data.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Array of predictions
            
        Raises:
            RuntimeError: If model not trained
            ValueError: If features don't match training data
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")
        
        if self.scaler is None:
            raise RuntimeError("Scaler not initialized.")
        
        # Validate features
        if list(X.columns) != self.feature_names:
            missing = set(self.feature_names) - set(X.columns)
            extra = set(X.columns) - set(self.feature_names)
            raise ValueError(
                f"Feature mismatch. Missing: {missing}, Extra: {extra}"
            )
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_with_stats(
        self,
        X: pd.DataFrame,
        region: str = "Unknown"
    ) -> Tuple[np.ndarray, Dict]:
        """Predict with statistical summary.
        
        Args:
            X: Feature DataFrame
            region: Region name for logging
            
        Returns:
            Tuple of (predictions, statistics_dict)
        """
        predictions = self.predict(X)
        
        stats = {
            'region': region,
            'count': len(predictions),
            'min': float(np.min(predictions)),
            'max': float(np.max(predictions)),
            'mean': float(np.mean(predictions)),
            'median': float(np.median(predictions)),
            'std': float(np.std(predictions)),
            'q25': float(np.percentile(predictions, 25)),
            'q75': float(np.percentile(predictions, 75))
        }
        
        logger.info(
            f"Region {region}: Mean={stats['mean']:.0f}, "
            f"Range=[{stats['min']:.0f}, {stats['max']:.0f}]"
        )
        
        return predictions, stats
    
    def feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """Get feature importance ranking.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature names and importance scores
            
        Raises:
            RuntimeError: If model not trained
        """
        if self.model is None:
            raise RuntimeError("Model not trained.")
        
        importance_scores = self.model.feature_importances_
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance_scores
        }).sort_values('importance', ascending=False)
        
        logger.debug(f"Top {top_n} features computed")
        return importance_df.head(top_n)
    
    def save_model(self, name: str = "forecaster") -> Path:
        """Save trained model to disk.
        
        Args:
            name: Model name (without extension)
            
        Returns:
            Path to saved model
            
        Raises:
            RuntimeError: If model not trained
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not trained.")
        
        model_file = self.model_dir / f"{name}_model.pkl"
        scaler_file = self.model_dir / f"{name}_scaler.pkl"
        features_file = self.model_dir / f"{name}_features.pkl"
        
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        if self.feature_names:
            with open(features_file, 'wb') as f:
                pickle.dump(self.feature_names, f)
        
        logger.info(f"Model saved: {model_file}")
        return model_file
    
    def load_model(self, name: str = "forecaster") -> None:
        """Load model from disk.
        
        Args:
            name: Model name (without extension)
            
        Raises:
            FileNotFoundError: If model files not found
        """
        model_file = self.model_dir / f"{name}_model.pkl"
        scaler_file = self.model_dir / f"{name}_scaler.pkl"
        features_file = self.model_dir / f"{name}_features.pkl"
        
        if not model_file.exists() or not scaler_file.exists():
            raise FileNotFoundError(f"Model files not found")
        
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_file, 'rb') as f:
            self.scaler = pickle.load(f)
        
        if features_file.exists():
            with open(features_file, 'rb') as f:
                self.feature_names = pickle.load(f)
        
        logger.info(f"Model loaded: {model_file}")
