"""Standalone ML module tests without app dependencies.

Run: python test_ml_standalone.py
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory

# Direct imports without app dependencies
import importlib.util

def load_module(module_name, file_path):
    """Load module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
dataset_loader_mod = load_module(
    "dataset_loader",
    "app/ml/dataset_loader.py"
)
demand_forecasting_mod = load_module(
    "demand_forecasting",
    "app/ml/demand_forecasting.py"
)

DatasetLoader = dataset_loader_mod.DatasetLoader
DatasetConfig = dataset_loader_mod.DatasetConfig
FeatureEngineer = dataset_loader_mod.FeatureEngineer
DemandForecaster = demand_forecasting_mod.DemandForecaster
ModelConfig = demand_forecasting_mod.ModelConfig
ModelMetrics = demand_forecasting_mod.ModelMetrics


def test_feature_engineer():
    """Test FeatureEngineer class."""
    print("\n[TEST 1] FeatureEngineer - Temporal Features")
    engineer = FeatureEngineer(random_seed=42)
    
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'value': np.random.randn(10)
    })
    
    result = engineer.extract_temporal_features(df, 'date')
    assert 'month' in result.columns
    assert 'day_of_week' in result.columns
    print("[OK] Temporal features extracted")


def test_feature_encoding():
    """Test categorical feature encoding."""
    print("\n[TEST 2] FeatureEngineer - Categorical Encoding")
    engineer = FeatureEngineer()
    
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'region': ['North', 'South', 'North', 'East']
    })
    
    result = engineer.encode_categorical_features(df)
    assert result.shape[1] > df.shape[1]
    print("[OK] Categorical features encoded")


def test_missing_values():
    """Test missing value handling."""
    print("\n[TEST 3] FeatureEngineer - Missing Values")
    engineer = FeatureEngineer()
    
    df = pd.DataFrame({
        'numeric': [1.0, np.nan, 3.0, 4.0],
        'categorical': ['A', None, 'B', 'A']
    })
    
    result = engineer.handle_missing_values(df, strategy='mean')
    assert not result.isna().any().any()
    print("[OK] Missing values handled")


def test_dataset_loader_init():
    """Test DatasetLoader initialization."""
    print("\n[TEST 4] DatasetLoader - Initialization")
    
    with TemporaryDirectory() as tmpdir:
        loader = DatasetLoader(data_dir=tmpdir)
        assert loader.config.data_directory == Path(tmpdir)
        print("[OK] DatasetLoader initialized")


def test_preprocess_data():
    """Test data preprocessing."""
    print("\n[TEST 5] DatasetLoader - Preprocessing")
    loader = DatasetLoader()
    
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=20),
        'value': np.random.randn(20),
        'category': np.random.choice(['A', 'B'], 20)
    })
    
    result = loader.preprocess_data(df)
    assert 'month' in result.columns
    print("[OK] Data preprocessed")


def test_prepare_features():
    """Test model feature preparation."""
    print("\n[TEST 6] DatasetLoader - Feature Preparation")
    loader = DatasetLoader()
    
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'sales': np.random.uniform(100, 5000, 100),
        'region': np.random.choice(['North', 'South'], 100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })
    
    df = loader.preprocess_data(df)
    X, y = loader.prepare_model_features(df, target_column='sales')
    
    assert X.shape[0] == 100
    assert len(y) == 100
    assert X.shape[1] > 0
    print("[OK] Model features prepared")


def test_model_config():
    """Test ModelConfig."""
    print("\n[TEST 7] ModelConfig - Initialization")
    config = ModelConfig(n_estimators=50, learning_rate=0.05)
    
    assert config.n_estimators == 50
    assert config.learning_rate == 0.05
    print("[OK] ModelConfig created")


def test_model_metrics():
    """Test ModelMetrics."""
    print("\n[TEST 8] ModelMetrics - Creation")
    metrics = ModelMetrics(
        rmse=250.0,
        r2_score=0.82,
        mape=12.5,
        n_samples=1000,
        n_features=50
    )
    
    assert metrics.rmse == 250.0
    str_repr = str(metrics)
    assert "RMSE" in str_repr
    print("[OK] ModelMetrics created")


def test_forecaster_init():
    """Test DemandForecaster initialization."""
    print("\n[TEST 9] DemandForecaster - Initialization")
    
    with TemporaryDirectory() as tmpdir:
        config = ModelConfig(n_estimators=50)
        forecaster = DemandForecaster(config=config, model_dir=tmpdir)
        
        assert forecaster.config.n_estimators == 50
        print("[OK] DemandForecaster initialized")


def test_train_model():
    """Test model training."""
    print("\n[TEST 10] DemandForecaster - Training")
    
    # Create sample data
    np.random.seed(42)
    X = pd.DataFrame({
        f'feature_{i}': np.random.randn(100)
        for i in range(10)
    })
    y = pd.Series(np.random.uniform(100, 5000, 100), name='sales')
    
    with TemporaryDirectory() as tmpdir:
        forecaster = DemandForecaster(model_dir=tmpdir)
        metrics = forecaster.train(X, y, verbose=False)
        
        assert isinstance(metrics, ModelMetrics)
        assert metrics.rmse > 0
        assert forecaster.model is not None
        print(f"[OK] Model trained: {metrics}")


def test_predict():
    """Test predictions."""
    print("\n[TEST 11] DemandForecaster - Predictions")
    
    # Create and train
    np.random.seed(42)
    X = pd.DataFrame({
        f'feature_{i}': np.random.randn(100)
        for i in range(10)
    })
    y = pd.Series(np.random.uniform(100, 5000, 100))
    
    with TemporaryDirectory() as tmpdir:
        forecaster = DemandForecaster(model_dir=tmpdir)
        forecaster.train(X, y, verbose=False)
        
        # Predict
        predictions = forecaster.predict(X.head(10))
        assert len(predictions) == 10
        print(f"[OK] Predictions made: {len(predictions)} samples")


def test_predict_with_stats():
    """Test predictions with statistics."""
    print("\n[TEST 12] DemandForecaster - Predictions with Stats")
    
    # Create and train
    np.random.seed(42)
    X = pd.DataFrame({
        f'feature_{i}': np.random.randn(100)
        for i in range(10)
    })
    y = pd.Series(np.random.uniform(100, 5000, 100))
    
    with TemporaryDirectory() as tmpdir:
        forecaster = DemandForecaster(model_dir=tmpdir)
        forecaster.train(X, y, verbose=False)
        
        # Predict with stats
        preds, stats = forecaster.predict_with_stats(X.head(20), region='Tamil Nadu')
        assert len(preds) == 20
        assert stats['region'] == 'Tamil Nadu'
        assert 'mean' in stats
        print(f"[OK] Stats computed: Mean={stats['mean']:.0f}, Std={stats['std']:.0f}")


def test_feature_importance():
    """Test feature importance."""
    print("\n[TEST 13] DemandForecaster - Feature Importance")
    
    # Create and train
    np.random.seed(42)
    X = pd.DataFrame({
        f'feature_{i}': np.random.randn(100)
        for i in range(10)
    })
    y = pd.Series(np.random.uniform(100, 5000, 100))
    
    with TemporaryDirectory() as tmpdir:
        forecaster = DemandForecaster(model_dir=tmpdir)
        forecaster.train(X, y, verbose=False)
        
        importance = forecaster.feature_importance(top_n=5)
        assert len(importance) <= 5
        print(f"[OK] Top 5 features extracted")


def test_save_load_model():
    """Test model persistence."""
    print("\n[TEST 14] DemandForecaster - Save/Load Model")
    
    # Create and train
    np.random.seed(42)
    X = pd.DataFrame({
        f'feature_{i}': np.random.randn(100)
        for i in range(10)
    })
    y = pd.Series(np.random.uniform(100, 5000, 100))
    
    with TemporaryDirectory() as tmpdir:
        # Save
        fc1 = DemandForecaster(model_dir=tmpdir)
        fc1.train(X, y, verbose=False)
        fc1.save_model("test")
        
        # Load
        fc2 = DemandForecaster(model_dir=tmpdir)
        fc2.load_model("test")
        
        # Compare
        pred1 = fc1.predict(X.head(5))
        pred2 = fc2.predict(X.head(5))
        
        np.testing.assert_array_almost_equal(pred1, pred2)
        print("[OK] Model saved and loaded successfully")


def test_full_pipeline():
    """Test complete ML pipeline."""
    print("\n[TEST 15] Full Pipeline - End-to-End")
    
    # Create data
    np.random.seed(42)
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=200),
        'sales': np.random.uniform(100, 5000, 200),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 200),
        'category': np.random.choice(['A', 'B', 'C'], 200),
    })
    
    with TemporaryDirectory() as tmpdir:
        # Load and preprocess
        loader = DatasetLoader(data_dir=tmpdir)
        df_proc = loader.preprocess_data(df)
        
        # Prepare features
        X, y = loader.prepare_model_features(df_proc)
        
        # Train
        fc = DemandForecaster(model_dir=tmpdir)
        metrics = fc.train(X, y, verbose=False)
        
        # Predict
        preds = fc.predict(X.head(50))
        preds_stats, stats = fc.predict_with_stats(X.head(50), 'TN')
        
        # Save
        fc.save_model("pipeline_test")
        
        # Load
        fc2 = DemandForecaster(model_dir=tmpdir)
        fc2.load_model("pipeline_test")
        
        print(f"[OK] Full pipeline executed successfully")
        print(f"    - Preprocessed: {df_proc.shape}")
        print(f"    - Features: {X.shape}")
        print(f"    - Model: {metrics}")


# Run all tests
if __name__ == "__main__":
    print("=" * 70)
    print("TWINAI ML MODULES - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("FeatureEngineer - Temporal", test_feature_engineer),
        ("FeatureEngineer - Encoding", test_feature_encoding),
        ("FeatureEngineer - Missing Values", test_missing_values),
        ("DatasetLoader - Init", test_dataset_loader_init),
        ("DatasetLoader - Preprocess", test_preprocess_data),
        ("DatasetLoader - Features", test_prepare_features),
        ("ModelConfig", test_model_config),
        ("ModelMetrics", test_model_metrics),
        ("DemandForecaster - Init", test_forecaster_init),
        ("DemandForecaster - Training", test_train_model),
        ("DemandForecaster - Predict", test_predict),
        ("DemandForecaster - Stats", test_predict_with_stats),
        ("DemandForecaster - Importance", test_feature_importance),
        ("DemandForecaster - Persistence", test_save_load_model),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"[FAILED] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n[SUCCESS] All ML modules tested successfully!")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {failed} tests failed")
        sys.exit(1)
