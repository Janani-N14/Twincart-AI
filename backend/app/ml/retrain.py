"""Retraining Pipeline for TwinCart AI Digital Twins.

Simulates scheduled or event-driven model updates:
1. Accepts new or appended transaction batches
2. Merges with historical synthetic_sales.csv
3. Re-fits the XGBoost demand model and regional seasonal time-series models
4. Updates metrics.json with updated backtest scores

Honest Architecture Note:
This operates via batch scheduled re-fitting (e.g. daily/weekly cron job or admin API trigger),
not a live continuous online streaming pipeline.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from app.ml.train import run_training

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SALES_CSV = DATA_DIR / "synthetic_sales.csv"


def append_new_sales_and_retrain(new_sales_df: Optional[pd.DataFrame] = None) -> dict:
    """Append new sales records to dataset and trigger model retraining.

    Args:
        new_sales_df: Optional DataFrame with new daily sales transactions.
                      If None, standard retraining on existing dataset is performed.

    Returns:
        Dictionary with updated model evaluation metrics.
    """
    logger.info("Retrain triggered at %s", datetime.now().isoformat())

    if new_sales_df is not None and not new_sales_df.empty:
        if SALES_CSV.exists():
            existing_df = pd.read_csv(SALES_CSV)
            combined_df = pd.concat([existing_df, new_sales_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(
                subset=["date", "region_id", "segment_id", "category"]
            ).sort_values("date")
            combined_df.to_csv(SALES_CSV, index=False)
            logger.info("Appended %d new records. Total records: %d", len(new_sales_df), len(combined_df))
        else:
            new_sales_df.to_csv(SALES_CSV, index=False)

    updated_metrics = run_training()
    updated_metrics["retrained_at"] = datetime.now().isoformat()
    logger.info("Retraining complete. New backtested MAPE: %s%%", updated_metrics.get("mape_percent"))
    return updated_metrics


if __name__ == "__main__":
    append_new_sales_and_retrain()
