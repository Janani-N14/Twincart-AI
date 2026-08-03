"""Dataset Loading Module - Manages Indian e-commerce Kaggle datasets.

This module provides clean OOP-based dataset management for loading,
preprocessing, and feature engineering from real Kaggle datasets.

Classes:
    DatasetLoader: Main class for dataset operations
    DatasetConfig: Configuration for dataset operations
    FeatureEngineer: Handles feature transformation
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DatasetConfig:
    """Configuration settings for dataset operations."""
    
    data_directory: Path
    kaggle_installed: bool
    random_seed: int = 42
    test_size: float = 0.2
    
    def __post_init__(self):
        """Ensure data directory exists."""
        self.data_directory.mkdir(parents=True, exist_ok=True)


class FeatureEngineer:
    """Handles feature engineering for ML models."""
    
    def __init__(self, random_seed: int = 42):
        """Initialize feature engineer.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def extract_temporal_features(self, df: pd.DataFrame, 
                                 date_column: Optional[str] = None) -> pd.DataFrame:
        """Extract time-based features from date columns.
        
        Args:
            df: DataFrame with date column
            date_column: Name of date column (auto-detect if None)
            
        Returns:
            DataFrame with added temporal features
        """
        df = df.copy()
        
        # Find date column
        if date_column is None:
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            if not date_cols:
                logger.warning("No date column found")
                return df
            date_column = date_cols[0]
        
        # Convert to datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # Extract features
        df['year'] = df[date_column].dt.year
        df['month'] = df[date_column].dt.month
        df['quarter'] = df[date_column].dt.quarter
        df['day_of_week'] = df[date_column].dt.dayofweek
        df['day_of_month'] = df[date_column].dt.day
        df['week_of_year'] = df[date_column].dt.isocalendar().week
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        logger.debug(f"Extracted temporal features from {date_column}")
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """One-hot encode categorical features.
        
        Args:
            df: DataFrame with categorical columns
            
        Returns:
            DataFrame with encoded categorical features
        """
        df = df.copy()
        
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
            logger.debug(f"Encoded {len(categorical_cols)} categorical columns")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """Handle missing values in dataset.
        
        Args:
            df: DataFrame with potential missing values
            strategy: 'mean', 'median', or 'forward_fill'
            
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        # Numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if strategy == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == 'median':
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == 'forward_fill':
                df[col].fillna(method='ffill', inplace=True)
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else "Unknown", 
                          inplace=True)
        
        logger.debug(f"Handled missing values using {strategy} strategy")
        return df


class DatasetLoader:
    """Main dataset loading and management class.
    
    Handles loading, preprocessing, and feature engineering of
    Indian e-commerce datasets from Kaggle.
    
    Attributes:
        config: DatasetConfig instance
        feature_engineer: FeatureEngineer instance
    """
    
    # Dataset metadata
    KAGGLE_DATASETS = {
        'store_data': {
            'id': 'abuhumzakhan/store-data',
            'size': '10K records',
            'description': 'Indian store sales data'
        },
        'ecommerce_sales': {
            'id': 'metaadata/ecommerce-sales-management',
            'size': 'Variable',
            'description': 'E-commerce transactions'
        },
        'store_item_demand': {
            'id': 'vik2012007/store-item-demand-forecasting-data',
            'size': 'Time series',
            'description': 'Store item demand data'
        }
    }
    
    # Indian regions
    REGIONS = [
        "North", "South", "East", "West", "Northeast"
    ]
    
    STATES = [
        "Tamil Nadu", "Bihar", "Kerala", "Uttar Pradesh",
        "Maharashtra", "West Bengal", "Rajasthan", "Gujarat",
        "Punjab", "Karnataka", "Andhra Pradesh", "Telangana"
    ]
    
    def __init__(self, data_dir: Optional[Path | str] = None):
        """Initialize DatasetLoader.
        
        Args:
            data_dir: Optional custom data directory
        """
        data_path = (
            Path(data_dir) if data_dir 
            else Path.home() / ".cache" / "twinai_datasets"
        )
        
        # Check Kaggle availability
        try:
            import kaggle
            kaggle_available = True
        except ImportError:
            kaggle_available = False
        
        self.config = DatasetConfig(
            data_directory=data_path,
            kaggle_installed=kaggle_available
        )
        self.feature_engineer = FeatureEngineer(
            random_seed=self.config.random_seed
        )
        
        logger.info(f"DatasetLoader initialized: {self.config.data_directory}")
    
    def load_indian_store_data(self) -> pd.DataFrame:
        """Load Indian Store Data from Kaggle or cache.
        
        Returns:
            DataFrame with store data
            
        Raises:
            FileNotFoundError: If dataset unavailable
        """
        dataset_name = 'store_data'
        cache_path = self.config.data_directory / dataset_name
        
        # Check cache
        csv_files = list(cache_path.glob("*.csv"))
        if csv_files:
            logger.info(f"Loading cached {dataset_name} data")
            return pd.read_csv(csv_files[0])
        
        # Download from Kaggle
        if not self.config.kaggle_installed:
            raise FileNotFoundError(
                f"Dataset not cached. Install Kaggle: pip install kaggle"
            )
        
        logger.info(f"Downloading {dataset_name}...")
        try:
            import kaggle
            kaggle.api.dataset_download_files(
                self.KAGGLE_DATASETS[dataset_name]['id'],
                path=cache_path,
                unzip=True
            )
        except Exception as e:
            raise FileNotFoundError(f"Download failed: {e}")
        
        csv_files = list(cache_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No CSV found after download")
        
        return pd.read_csv(csv_files[0])
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess raw dataset.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        df = df.copy()
        
        # Handle missing values
        df = self.feature_engineer.handle_missing_values(df)
        
        # Extract temporal features
        df = self.feature_engineer.extract_temporal_features(df)
        
        logger.info(f"Preprocessed: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def prepare_model_features(
        self,
        df: pd.DataFrame,
        target_column: str = "sales",
        region_filter: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target for ML models.
        
        Args:
            df: Preprocessed DataFrame
            target_column: Name of target variable
            region_filter: Optional region to filter by
            
        Returns:
            Tuple of (X_features, y_target)
        """
        df = df.copy()
        
        # Filter by region if specified
        if region_filter:
            region_cols = [c for c in df.columns 
                          if any(x in c.lower() for x in ['region', 'state', 'city'])]
            for col in region_cols:
                mask = df[col].astype(str).str.contains(
                    region_filter, case=False, na=False
                )
                if mask.any():
                    df = df[mask]
                    logger.info(f"Filtered to {len(df)} records for {region_filter}")
                    break
        
        # Find and extract target
        target_cols = [c for c in df.columns 
                      if target_column.lower() in c.lower()]
        if not target_cols:
            raise ValueError(f"Target column '{target_column}' not found")
        
        target_col = target_cols[0]
        y = df[target_col].copy()
        
        # Encode categorical features
        df_encoded = self.feature_engineer.encode_categorical_features(df)
        
        # Select features
        exclude_cols = {target_col}
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        exclude_cols.update(date_cols)
        
        feature_cols = [c for c in df_encoded.columns 
                       if c not in exclude_cols]
        X = df_encoded[feature_cols].fillna(0)
        
        logger.info(f"Model features: {X.shape[1]} features, {len(X)} samples")
        return X, y
    
    def get_dataset_info(self) -> Dict[str, Dict]:
        """Get information about available datasets.
        
        Returns:
            Dictionary with dataset information
        """
        info = {}
        for dataset_name, dataset_dir in [(name, self.config.data_directory / name) 
                                         for name in self.KAGGLE_DATASETS.keys()]:
            if dataset_dir.exists():
                csv_files = list(dataset_dir.glob("*.csv"))
                if csv_files:
                    df = pd.read_csv(csv_files[0])
                    info[dataset_name] = {
                        'status': 'available',
                        'records': len(df),
                        'columns': df.shape[1],
                        'path': str(csv_files[0])
                    }
        
        logger.debug(f"Available datasets: {list(info.keys())}")
        return info
