import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def load_and_preprocess_data(data_dir="sea"):
    """
    Load actuals, forecast, and spatial data for Seattle.
    Merge them into a single training dataframe.
    """
    print("Loading actuals data...")
    actuals_file = list(Path(data_dir).glob("sea_actuals_*_merged.csv"))[0]
    actuals = pd.read_csv(actuals_file)
    actuals['observed_at'] = pd.to_datetime(actuals['observed_at'])
    actuals = actuals.sort_values('observed_at').drop_duplicates('observed_at', keep='last')
    
    print("Loading forecast data...")
    forecast_file = list(Path(data_dir).glob("sea_forecast_*.csv"))[0]
    forecast = pd.read_csv(forecast_file)
    forecast['forecast_time_utc'] = pd.to_datetime(forecast['forecast_time_utc'])
    forecast = forecast.sort_values('forecast_time_utc').drop_duplicates('forecast_time_utc', keep='last')
    
    print("Loading spatial data...")
    spatial_file = list(Path(data_dir).glob("sea_spatial_*.csv"))[0]
    spatial = pd.read_csv(spatial_file)
    spatial['observed_at'] = pd.to_datetime(spatial['observed_at'])
    
    # Calculate daily max temperature (target variable)
    actuals['local_date'] = pd.to_datetime(actuals['target_date'])
    daily_max = actuals.groupby('local_date')['temp_c'].max().reset_index()
    daily_max.rename(columns={'temp_c': 'target_max_temp'}, inplace=True)
    
    # Feature engineering from forecast
    # We aggregate daily forecast features
    forecast['local_date'] = forecast['forecast_time_utc'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.normalize().dt.tz_localize(None)
    forecast_daily = forecast.groupby('local_date').agg({
        'temperature_2m': ['min', 'max', 'mean'],
        'relative_humidity_2m': ['mean'],
        'wind_speed_10m': ['mean', 'max'],
        'precipitation': ['sum'],
        'cloud_cover': ['mean']
    }).reset_index()
    
    # Flatten multi-level columns
    forecast_daily.columns = ['local_date'] + [f"{col[0]}_{col[1]}" for col in forecast_daily.columns[1:]]
    
    # Merge targets and features
    merged = pd.merge(daily_max, forecast_daily, on='local_date', how='inner')
    
    merged = merged.dropna()
    print(f"Prepared {len(merged)} days of training data.")
    return merged

if __name__ == "__main__":
    df = load_and_preprocess_data()
    df.to_csv("train/processed_training_data.csv", index=False)
    print("Saved processed data to train/processed_training_data.csv")
