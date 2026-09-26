"""Comprehensive tests for ML modules - OOP-based implementation.

Tests verify:
- Dataset loading and preprocessing
- Demand forecasting model training and prediction
- Image generation interface
- Integration workflows
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory

from app.ml.dataset_loader import DatasetLoader, FeatureEngineer, DatasetConfig
from app.ml.demand_forecasting import DemandForecaster, ModelConfig, ModelMetrics


class TestFeatureEngineer:
    """Tests for FeatureEngineer class."""
    
    def test_initialization(self):
        """Test FeatureEngineer initialization."""
        engineer = FeatureEngineer(random_seed=42)
        assert engineer.random_seed == 42
    
    def test_temporal_features(self):
        """Test temporal feature extraction."""
        engineer = FeatureEngineer()
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': np.random.randn(10)
        })
        
        result = engineer.extract_temporal_features(df, 'date')
        
        assert 'month' in result.columns
        assert 'day_of_week' in result.columns
        assert 'quarter' in result.columns
        assert 'is_weekend' in result.columns
    
    def test_categorical_encoding(self):
        """Test categorical feature encoding."""
        engineer = FeatureEngineer()
        
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C'],
            'region': ['North', 'South', 'North', 'East']
        })
        
        result = engineer.encode_categorical_features(df)
        
        # Should have more columns after one-hot encoding
        assert result.shape[1] > df.shape[1]
    
    def test_missing_values_handling(self):
        """Test missing value imputation."""
        engineer = FeatureEngineer()
        
        df = pd.DataFrame({
            'numeric': [1.0, np.nan, 3.0, 4.0],
            'categorical': ['A', None, 'B', 'A']
        })
        
        result = engineer.handle_missing_values(df, strategy='mean')
        
        assert not result.isna().any().any()


class TestDatasetConfig:
    """Tests for DatasetConfig dataclass."""
    
    def test_config_creation(self, tmp_path):
        """Test DatasetConfig instantiation."""
        config = DatasetConfig(
            data_directory=tmp_path,
            kaggle_installed=False
        )
        
        assert config.data_directory == tmp_path
        assert config.kaggle_installed is False
        assert tmp_path.exists()
    
    def test_config_defaults(self, tmp_path):
        """Test DatasetConfig default values."""
        config = DatasetConfig(
            data_directory=tmp_path,
            kaggle_installed=False
        )
        
        assert config.random_seed == 42
        assert config.test_size == 0.2


class TestDatasetLoader:
    """Tests for DatasetLoader class."""
    
    def test_initialization_default(self):
        """Test DatasetLoader with default settings."""
        loader = DatasetLoader()
        assert loader.config.data_directory == Path.home() / ".cache" / "twinai_datasets"
    
    def test_initialization_custom(self, tmp_path):
        """Test DatasetLoader with custom directory."""
        loader = DatasetLoader(data_dir=tmp_path)
        assert loader.config.data_directory == tmp_path
    
    def test_feature_engineer_available(self):
        """Test FeatureEngineer is initialized."""
        loader = DatasetLoader()
        assert loader.feature_engineer is not None
        assert isinstance(loader.feature_engineer, FeatureEngineer)
    
    def test_preprocess_data(self):
        """Test data preprocessing."""
        loader = DatasetLoader()
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': np.random.randn(10),
            'category': ['A', 'B'] * 5
        })
        
        result = loader.preprocess_data(df)
        
        assert 'month' in result.columns
        assert 'day_of_week' in result.columns
        assert len(result) == len(df)
    
    def test_prepare_model_features(self):
        """Test feature preparation for modeling."""
        loader = DatasetLoader()
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'sales': np.random.uniform(100, 5000, 100),
            'region': np.random.choice(['North', 'South'], 100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Preprocess first
        df = loader.preprocess_data(df)
        
        # Prepare features
        X, y = loader.prepare_model_features(df, target_column='sales')
        
        assert X.shape[0] == len(df)
        assert len(y) == len(df)
        assert X.shape[1] > 0
    
    def test_prepare_features_with_region_filter(self):
        """Test feature preparation with region filtering."""
        loader = DatasetLoader()
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'sales': np.random.uniform(100, 5000, 100),
            'region': np.random.choice(['North', 'South'], 100),
        })
        
        df = loader.preprocess_data(df)
        X, y = loader.prepare_model_features(
            df, target_column='sales', region_filter='North'
        )
        
        assert len(X) <= 100
    
    def test_dataset_info(self, tmp_path):
        """Test getting dataset information."""
        loader = DatasetLoader(data_dir=tmp_path)
        info = loader.get_dataset_info()
        
        assert isinstance(info, dict)


class TestModelConfig:
    """Tests for ModelConfig dataclass."""
    
    def test_default_config(self):
        """Test ModelConfig default values."""
        config = ModelConfig()
        
        assert config.n_estimators == 100
        assert config.max_depth == 6
        assert config.learning_rate == 0.1
        assert config.test_size == 0.2
    
    def test_custom_config(self):
        """Test ModelConfig with custom values."""
        config = ModelConfig(n_estimators=50, learning_rate=0.05)
        
        assert config.n_estimators == 50
        assert config.learning_rate == 0.05
        assert config.max_depth == 6  # Default unchanged


class TestModelMetrics:
    """Tests for ModelMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test ModelMetrics creation."""
        metrics = ModelMetrics(
            rmse=250.5,
            r2_score=0.82,
            mape=12.5,
            n_samples=1000,
            n_features=50
        )
        
        assert metrics.rmse == 250.5
        assert metrics.r2_score == 0.82
        assert metrics.mape == 12.5
    
    def test_metrics_str_representation(self):
        """Test ModelMetrics string representation."""
        metrics = ModelMetrics(
            rmse=250.0,
            r2_score=0.82,
            mape=12.5,
            n_samples=1000,
            n_features=50
        )
        
        str_repr = str(metrics)
        assert "RMSE" in str_repr
        assert "R2" in str_repr
        assert "MAPE" in str_repr


class TestDemandForecaster:
    """Tests for DemandForecaster class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        np.random.seed(42)
        n = 200
        
        X = pd.DataFrame({
            f'feature_{i}': np.random.randn(n)
            for i in range(10)
        })
        y = pd.Series(
            np.random.uniform(100, 5000, n),
            name='sales'
        )
        
        return X, y
    
    def test_initialization_default(self):
        """Test DemandForecaster default initialization."""
        forecaster = DemandForecaster()
        
        assert forecaster.config is not None
        assert forecaster.model is None
        assert forecaster.scaler is None
    
    def test_initialization_custom(self, tmp_path):
        """Test DemandForecaster custom initialization."""
        config = ModelConfig(n_estimators=50)
        forecaster = DemandForecaster(config=config, model_dir=tmp_path)
        
        assert forecaster.config.n_estimators == 50
        assert forecaster.model_dir == tmp_path
    
    def test_train_model(self, sample_data):
        """Test model training."""
        X, y = sample_data
        forecaster = DemandForecaster()
        
        metrics = forecaster.train(X, y, verbose=False)
        
        assert isinstance(metrics, ModelMetrics)
        assert metrics.rmse > 0
        assert metrics.r2_score <= 1.0
        assert forecaster.model is not None
    
    def test_train_empty_data(self):
        """Test training with empty data raises error."""
        forecaster = DemandForecaster()
        
        with pytest.raises(ValueError):
            forecaster.train(pd.DataFrame(), pd.Series())
    
    def test_predict_before_train(self, sample_data):
        """Test predict before train raises error."""
        X, y = sample_data
        forecaster = DemandForecaster()
        
        with pytest.raises(RuntimeError):
            forecaster.predict(X.head(5))
    
    def test_predict_after_train(self, sample_data):
        """Test predictions after training."""
        X, y = sample_data
        forecaster = DemandForecaster()
        forecaster.train(X, y, verbose=False)
        
        predictions = forecaster.predict(X.head(10))
        
        assert len(predictions) == 10
        assert all(isinstance(p, (int, float, np.number)) for p in predictions)
    
    def test_predict_with_stats(self, sample_data):
        """Test predictions with statistics."""
        X, y = sample_data
        forecaster = DemandForecaster()
        forecaster.train(X, y, verbose=False)
        
        predictions, stats = forecaster.predict_with_stats(
            X.head(20), region='Tamil Nadu'
        )
        
        assert len(predictions) == 20
        assert stats['region'] == 'Tamil Nadu'
        assert 'mean' in stats
        assert 'std' in stats
        assert stats['min'] <= stats['mean'] <= stats['max']
    
    def test_feature_importance(self, sample_data):
        """Test feature importance extraction."""
        X, y = sample_data
        forecaster = DemandForecaster()
        forecaster.train(X, y, verbose=False)
        
        importance = forecaster.feature_importance(top_n=5)
        
        assert len(importance) <= 5
        assert 'feature' in importance.columns
        assert 'importance' in importance.columns
    
    def test_save_model(self, sample_data):
        """Test model persistence."""
        X, y = sample_data
        
        with TemporaryDirectory() as tmpdir:
            forecaster = DemandForecaster(model_dir=tmpdir)
            forecaster.train(X, y, verbose=False)
            
            path = forecaster.save_model("test")
            assert path.exists()
    
    def test_load_model(self, sample_data):
        """Test model loading."""
        X, y = sample_data
        
        with TemporaryDirectory() as tmpdir:
            # Save
            forecaster1 = DemandForecaster(model_dir=tmpdir)
            forecaster1.train(X, y, verbose=False)
            forecaster1.save_model("test")
            
            # Load
            forecaster2 = DemandForecaster(model_dir=tmpdir)
            forecaster2.load_model("test")
            
            # Compare predictions
            pred1 = forecaster1.predict(X.head(5))
            pred2 = forecaster2.predict(X.head(5))
            
            np.testing.assert_array_almost_equal(pred1, pred2)


class TestIntegration:
    """Integration tests for full workflows."""
    
    def test_full_pipeline(self):
        """Test complete dataset -> features -> training -> predictions."""
        # Create sample data
        np.random.seed(42)
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=200),
            'sales': np.random.uniform(100, 5000, 200),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 200),
            'category': np.random.choice(['A', 'B', 'C'], 200),
        })
        
        # Load and preprocess
        loader = DatasetLoader()
        df_processed = loader.preprocess_data(df)
        
        # Prepare features
        X, y = loader.prepare_model_features(df_processed)
        
        # Train model
        forecaster = DemandForecaster()
        metrics = forecaster.train(X, y, verbose=False)
        
        # Make predictions
        predictions = forecaster.predict(X.head(50))
        predictions_with_stats, stats = forecaster.predict_with_stats(
            X.head(50), region='Tamil Nadu'
        )
        
        # Verify results
        assert metrics.r2_score > -1  # Should have some predictive power
        assert len(predictions) == 50
        assert len(predictions_with_stats) == 50
        assert stats['count'] == 50


class TestImageGeneration:
    """Tests for PosterGenerator class (basic, no GPU required)."""
    
    def test_initialization(self):
        """Test PosterGenerator initialization."""
        try:
            from app.ml.image_generation import PosterGenerator
            
            gen = PosterGenerator(device="cpu")
            assert gen.output_dir == Path.home() / ".cache" / "twinai_posters"
        except ImportError:
            pytest.skip("Image generation dependencies not installed")
    
    def test_categories_defined(self):
        """Test category definitions."""
        try:
            from app.ml.image_generation import PosterGenerator
            
            gen = PosterGenerator(device="cpu")
            assert len(gen.CATEGORIES) > 0
            assert 'apparel' in gen.CATEGORIES
        except ImportError:
            pytest.skip("Image generation dependencies not installed")
    
    def test_regions_defined(self):
        """Test region definitions."""
        try:
            from app.ml.image_generation import PosterGenerator
            
            gen = PosterGenerator(device="cpu")
            assert len(gen.REGIONS) > 0
            assert 'Tamil Nadu' in gen.REGIONS
        except ImportError:
            pytest.skip("Image generation dependencies not installed")
