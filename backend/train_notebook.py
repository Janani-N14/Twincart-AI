"""
TwinCart AI Model Training & Image Generation Notebook
=================================================

This script demonstrates end-to-end training and usage:
1. Load/generate Indian e-commerce sales data
2. Train XGBoost demand forecasting model
3. Generate campaign posters with Stable Diffusion

Run with: python train_notebook.py

Or in Jupyter:
    %run train_notebook.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from app.ml.dataset_loader import DatasetLoader
from app.ml.demand_forecasting import DemandForecaster
from app.ml.image_generation import PosterGenerator


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def train_demand_forecasting():
    """Step 1: Train demand forecasting model."""
    section("STEP 1: TRAIN DEMAND FORECASTING MODEL")

    # Load data (synthetic or real Kaggle)
    print("📊 Loading Indian e-commerce sales data...")
    loader = DatasetLoader()
    df_sales = loader.generate_synthetic_sales_data(n_records=5000)

    print(f"Dataset shape: {df_sales.shape}")
    print(f"Date range: {df_sales['order_date'].min()} to {df_sales['order_date'].max()}")
    print(f"\nSample records:")
    print(df_sales.head(3))

    # Prepare features
    print("\n📈 Preparing features for model training...")
    X, y = loader.get_features_for_model(df_sales, target_region=None)
    print(f"Features: {X.shape[1]} columns, {len(X)} samples")
    print(f"Top features: {list(X.columns[:5])}")

    # Train
    print("\n🤖 Training XGBoost model...")
    forecaster = DemandForecaster()
    metrics = forecaster.train(
        X, y,
        n_estimators=150,
        max_depth=7,
        learning_rate=0.1,
    )
    print(f"Training complete!")
    print(f"  RMSE: {metrics['rmse']}")
    print(f"  R² Score: {metrics['r2']}")
    print(f"  Training samples: {metrics['train_samples']}")
    print(f"  Test samples: {metrics['test_samples']}")

    # Feature importance
    print(f"\nTop 5 important features:")
    for feat, importance in forecaster.get_feature_importance(top_n=5).items():
        print(f"  {feat}: {importance:.4f}")

    # Save
    print("\n💾 Saving trained model...")
    forecaster.save()
    print("✅ Model saved!")

    return forecaster, df_sales


def generate_posters():
    """Step 2: Generate campaign posters with Stable Diffusion."""
    section("STEP 2: GENERATE CAMPAIGN POSTERS")

    print("🎨 Initializing Stable Diffusion model...")
    print("   First run will download ~8–12 GB model (5–10 minutes).")
    print("   Requires GPU with 8GB+ VRAM (can use CPU but slow).\n")

    try:
        generator = PosterGenerator(
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            device="auto",
            use_half_precision=True,
        )
        print("✅ Model loaded!\n")
    except ImportError as e:
        print(f"❌ ML dependencies not installed:")
        print(f"   pip install -r requirements_ml.txt")
        return

    # Example prompts for Indian e-commerce
    prompts = [
        "Indian festival e-commerce poster, cotton sarees and kurtas, Diwali lamps, "
        "vibrant golds and reds, professional design, mobile-optimized",

        "Budget-friendly apparel sale poster, diverse Indian customers, ethnic wear, "
        "bright colors, festive mood, commerce banner design",

        "Electronics sale poster, mobile phones and accessories, tech aesthetic, "
        "modern design, Indian text overlay area, professional",
    ]

    print("🖼️  Generating 3 sample campaign posters...\n")

    output_dir = Path(__file__).parent / "generated_posters"
    output_dir.mkdir(exist_ok=True)

    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/3] Generating: {prompt[:60]}...")
        try:
            image = generator.generate(
                prompt=prompt,
                height=768,
                width=512,
                num_steps=25,
                guidance_scale=7.5,
            )
            output_file = output_dir / f"poster_{i}.png"
            generator.save_poster(image, output_file)
            print(f"      ✅ Saved to {output_file}")
        except Exception as e:
            print(f"      ❌ Error: {e}")

    print(f"\n✅ Posters saved to {output_dir}")


def predict_sample():
    """Step 3: Use trained model for predictions."""
    section("STEP 3: MAKE PREDICTIONS WITH TRAINED MODEL")

    # Load model
    forecaster = DemandForecaster()
    if not forecaster.load():
        print("⚠️  No saved model found. Train first!")
        return

    # Generate new sample data
    loader = DatasetLoader()
    df_new = loader.generate_synthetic_sales_data(n_records=100)
    X_new, _ = loader.get_features_for_model(df_new)

    # Predict
    print("🔮 Making demand predictions...")
    predictions = forecaster.predict(X_new)

    print(f"\nPredictions summary:")
    print(f"  Mean: ₹{predictions.mean():.2f}")
    print(f"  Std Dev: ₹{predictions.std():.2f}")
    print(f"  Min: ₹{predictions.min():.2f}")
    print(f"  Max: ₹{predictions.max():.2f}")

    print(f"\nSample predictions (first 5):")
    for i, pred in enumerate(predictions[:5]):
        print(f"  {i+1}. ₹{pred:.2f}")


def main():
    """Run the full training pipeline."""
    section("TwinCart AI MODEL TRAINING & IMAGE GENERATION")

    print("This notebook demonstrates:")
    print("  1. Train demand forecasting model on Indian e-commerce data")
    print("  2. Generate campaign posters using Stable Diffusion")
    print("  3. Make predictions with the trained model\n")

    # Step 1: Train
    forecaster, df_sales = train_demand_forecasting()

    # Step 2: Generate posters (optional — slow)
    generate_posters_yn = input("\nGenerate campaign posters? (y/n, requires GPU): ").lower()
    if generate_posters_yn == "y":
        generate_posters()

    # Step 3: Predict
    predict_sample()

    section("COMPLETE!")
    print("✅ All done!\n")
    print("Next steps:")
    print("  1. Start the TwinCart AI backend: uvicorn app.main:app --reload")
    print("  2. Use POST /api/training/train-demand-forecast to train via API")
    print("  3. Use POST /api/training/generate-poster to generate posters")
    print("  4. Check POST /api/campaigns/generate for full pipeline with posters\n")


if __name__ == "__main__":
    main()
