# Seattle Temperature Prediction & Polymarket Dashboard

This project is aimed at forecasting the daily maximum temperature in Seattle using a blended Stack Model of **Long Short-Term Memory (LSTM)** neural networks and **LightGBM**. It combines this precision forecasting with live betting opportunities available on Polymarket.

## Project Architecture

- `main.py`: The entry point script to check dependencies and boot up the system.
- `app.py`: A high-performance Streamlit dashboard for data monitoring and signal execution.
- `data_fetcher.py`: Connects to aviationweather NOAA API (METAR) to pull real-time weather metrics, stored in a minimal `app_database.db`.
- `market_fetcher.py`: Analyzes active events on Polymarket to match temperature bounds alongside generated predictions.
- `train/`: Contains all intermediate state files (`.pkl`, `.pth`) and the machine learning pipeline code (`train_pipeline.py`, `data_preprocessing.py`).

## Installation & Running

1. Ensure Python 3.10+ is installed.
2. Initialize and activate a virtual environment.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the dashboard application:
   ```bash
   python main.py
   ```

## Model Strategy

I use advanced Feature Engineering over 20+ signals (Cloud coverage, relative humidity, multi-altitude winds, etc). An **LSTM** sequence captures temporal non-linear auto-correlation effectively, mapping onto a **LightGBM** meta-learner to form our highest confidence stacking model.
